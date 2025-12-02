import streamlit as st
import pandas as pd
from src.calculators.psychrometrics_calculator import (
    calculate_psychrometric_properties,
    generate_psychrometric_chart
)
from src.utils.unit_manager import render_global_settings_sidebar, render_local_unit_override, convert_value, format_unit
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()

st.set_page_config(page_title="Psikrometrik Hesaplayıcı", page_icon="🌬️")
render_header("Psikrometrik Hesaplayıcı", "🌬️")
st.markdown("Bu modül, nemli havanın termodinamik özelliklerini (entalpi, nem oranı, çiğ noktası vs.) hesaplamanıza ve psikrometrik diyagram üretmenize yardımcı olur.")

st.divider()

# --- GİRİŞ ---
# Global Ayarlar
render_global_settings_sidebar()

# Yerel Ayarlar
unit_system, units = render_local_unit_override("psychro")

with st.expander("🧮 Giriş Parametreleri", expanded=True):
    p_unit = units.get('P', 'Pa')
    P_input = st.number_input(f"Atmosfer Basıncı ({format_unit(p_unit)})", value=101325.0)
    # SI'ya çevir
    P = convert_value(P_input, p_unit, 'Pa')
    
    t_unit = units.get('T', 'degC') # Psikrometri genelde C kullanır ama unit manager K dönebilir.
    # Eğer unit manager K dönerse, kullanıcı K girer, biz C'ye çevirip fonksiyona yollarız (fonksiyon C bekliyor olabilir mi? Hayır, fonksiyonun ne beklediğine bakalım)
    # calculate_psychrometric_properties(T_db_C, ...) -> T_db_C bekliyor.
    
    T_db_input = st.number_input(f"Kuru Termometre Sıcaklığı ({format_unit(t_unit)})", value=25.0)
    # Fonksiyon C bekliyor
    T_db_C = convert_value(T_db_input, t_unit, 'degC')

    method = st.radio("İkinci Bilinen Özellik:", ("Bağıl Nem (%)", f"Yaş Termometre Sıcaklığı ({format_unit(t_unit)})"))

    if method == "Bağıl Nem (%)":
        rh = st.slider("Bağıl Nem (%)", 0, 100, 50)
        T_wb = None
    else:
        rh = None
        T_wb_input = st.number_input(f"Yaş Termometre Sıcaklığı ({format_unit(t_unit)})", value=20.0)
        T_wb = convert_value(T_wb_input, t_unit, 'degC')

    if st.button("🔎 Hesapla"):
        try:
            props = calculate_psychrometric_properties(T_db_C, P, rh, T_wb)
            st.session_state.psychro_props = props
            st.session_state.psychro_P = P
            st.session_state.psychro_T = T_db_C
            st.session_state.psychro_units = units # Birimleri sakla
        except Exception as e:
            st.error(f"Hesaplama sırasında hata oluştu: {e}")
            st.session_state.psychro_props = None

# --- SONUÇLARI GÖSTER (Varsa) ---
props = st.session_state.get("psychro_props")
if props:
    if "Hata" in props:
        st.error(props["Hata"])
    else:
        st.subheader("📌 Hesaplanan Özellikler")

        units = st.session_state.get("psychro_units", units)
        t_unit = units.get('T', 'degC')
        vol_unit = units.get('Vol', 'm**3') # Özgül hacim m3/kg
        energy_unit = units.get('Energy', 'kJ') # Entalpi kJ/kg
        mass_unit = units.get('Mass', 'kg')
        
        # Çevrimler
        # props['T_wb (°C)'] -> t_unit
        twb_val = convert_value(props['T_wb (°C)'], 'degC', t_unit)
        tdp_val = convert_value(props['T_dp (°C)'], 'degC', t_unit)
        
        # h (kJ/kg_dry) -> energy_unit / mass_unit
        # Pint ile kJ/kg -> hedef
        h_val = convert_value(props['h (kJ/kg_dry)'], 'kJ/kg', f"{energy_unit}/{mass_unit}")
        
        # v (m³/kg_dry) -> vol_unit / mass_unit
        v_val = convert_value(props['v (m³/kg_dry)'], 'm**3/kg', f"{vol_unit}/{mass_unit}")
        
        col1, col2, col3 = st.columns(3)
        with col1: render_card("Yaş Termometre", f"{twb_val:.2f}", unit=format_unit(t_unit))
        with col2: render_card("Çiğ Noktası", f"{tdp_val:.2f}", unit=format_unit(t_unit))
        with col3: render_card("Bağıl Nem", f"{props['RH (%)']:.1f}", unit="%")

        col4, col5, col6 = st.columns(3)
        with col4: render_card("Nem Oranı", f"{props['w (kg_water/kg_dry)']:.5f}", unit="kg/kg")
        with col5: render_card("Entalpi", f"{h_val:.2f}", unit=f"{format_unit(energy_unit)}/{format_unit(mass_unit)} dry")
        with col6: render_card("Özgül Hacim", f"{v_val:.4f}", unit=f"{format_unit(vol_unit)}/{format_unit(mass_unit)}")

# --- PSİKROMETRİK DİYAGRAM ---
st.divider()
st.subheader("📉 Psikrometrik Diyagram")

if st.button("📊 Diyagramı Göster", key="show_diagram"):
    try:
        P_val = st.session_state.get("psychro_P", 101325.0)
        fig = generate_psychrometric_chart(P_val, T_min=0, T_max=50)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Diyagram oluşturulamadı: {e}")
