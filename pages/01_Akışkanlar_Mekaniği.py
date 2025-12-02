import streamlit as st
from src.calculators.fluids_calculator import calculate_reynolds, calculate_pressure_drop
from src.calculators.fluids_calculator import calculate_reynolds, calculate_pressure_drop
from src.calculators.thermo_calculator import calculate_properties as calculate_thermo_properties
from src.utils.unit_manager import render_global_settings_sidebar, render_local_unit_override, convert_value
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()

st.set_page_config(page_title="Akışkanlar Mekaniği", page_icon="💧")

# Başlık ve açıklama
render_header("Akışkanlar Mekaniği", "💧")
st.markdown("Bu modülde boru içi akışlar için Reynolds sayısı, sürtünme katsayısı ve basınç düşüşü gibi hesaplamaları yapabilirsiniz.")

# Başlangıç state
if 'density' not in st.session_state:
    st.session_state.density = 1000.0
if 'viscosity' not in st.session_state:
    st.session_state.viscosity = 0.001

st.divider()

# Global Ayarlar
render_global_settings_sidebar()

# Yerel Ayarlar
unit_system, units = render_local_unit_override("fluids")

# Calculator uyumluluğu
calc_unit_system = unit_system
if unit_system == "Metric":
    calc_unit_system = "Metric (CGS)"

mapped_manual_units = {}
if unit_system == "Manual":
    mapped_manual_units = {
        'rho': units.get('Density'),
        'mu': units.get('Viscosity'),
        'T': units.get('T'),
        'P': units.get('P')
    }

# --- AKIŞKAN ÖZELLİKLERİ ---
with st.expander("🧪 Akışkan Özelliklerini Hesapla veya Manuel Gir", expanded=True):
    render_info_card("Dilerseniz yaygın akışkanlardan birini seçerek sıcaklık ve basınca bağlı yoğunluk ve viskozite hesaplatabilirsiniz.")
    
    common_chemicals = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]
    chemical_name = st.selectbox("Akışkan Seç:", options=common_chemicals)
    
    col1, col2 = st.columns(2)
    with col1:
        t_unit = units.get('T', 'K')
        temp_input = st.number_input(f"Sıcaklık ({t_unit})", value=298.15)
        # Thermo calc expects input in the selected unit system, so we pass as is if unit system matches
        # But wait, calculate_properties takes input and unit_system.
        # If unit_system is "English", it expects F and psia.
        # So we just pass the input value and the unit system.
        
    with col2:
        p_unit = units.get('P', 'Pa')
        pressure_input = st.number_input(f"Basınç ({p_unit})", value=101325.0)
        
    if st.button("🎯 Akışkan Özelliklerini Getir"):
        try:
            # calculate_properties expects inputs in the unit_system's units
            df, _ = calculate_thermo_properties(
                chemical_name, temp_input, pressure_input, calc_unit_system, ["Yoğunluk (rho)", "Viskozite (mu)"], mapped_manual_units
            )
            rho_val = float(df.loc[df['Özellik'] == 'Yoğunluk (rho)', 'Değer'].iloc[0])
            mu_val = float(df.loc[df['Özellik'] == 'Viskozite (mu)', 'Değer'].iloc[0])
            
            st.session_state.density = rho_val
            st.session_state.viscosity = mu_val
            
            rho_unit = units.get('Density', 'kg/m**3')
            mu_unit = units.get('Viscosity', 'Pa*s')
            
            st.success(f"{chemical_name.title()} için: Yoğunluk = {rho_val:.4f} {rho_unit}, Viskozite = {mu_val:.6g} {mu_unit}")
        except Exception as e:
            st.error(f"Özellikler getirilemedi: {e}")

# --- GİRİŞ ---
st.divider()
st.subheader("🔧 Akışkan ve Boru Bilgileri")

col1, col2 = st.columns(2)
with col1:
    rho_unit = units.get('Density', 'kg/m**3')
    density_input = st.number_input(f"Yoğunluk ({rho_unit})", value=st.session_state.density, format="%.4f", key="density_input")
    # SI'ya çevir
    density = convert_value(density_input, rho_unit, 'kg/m**3')
    
    len_unit = units.get('Len', 'm')
    diameter_input = st.number_input(f"Boru İç Çapı ({len_unit})", value=0.1, format="%.4f")
    diameter = convert_value(diameter_input, len_unit, 'm')
with col2:
    vel_unit = units.get('Velocity', 'm/s')
    velocity_input = st.number_input(f"Hız ({vel_unit})", value=1.0, format="%.4f")
    velocity = convert_value(velocity_input, vel_unit, 'm/s')
    
    mu_unit = units.get('Viscosity', 'Pa*s')
    viscosity_input = st.number_input(f"Viskozite ({mu_unit})", value=st.session_state.viscosity, format="%.6g", key="viscosity_input")
    viscosity = convert_value(viscosity_input, mu_unit, 'Pa*s')

# --- HESAPLAMA ---
st.divider()
st.subheader("🧮 Hesaplama Parametreleri")

col1, col2 = st.columns(2)
with col1:
    len_unit = units.get('Len', 'm')
    length_input = st.number_input(f"Boru Uzunluğu ({len_unit})", value=100.0, format="%.2f")
    length = convert_value(length_input, len_unit, 'm')
with col2:
    roughness_input = st.number_input(f"Boru Pürüzlülüğü ({len_unit})", value=0.000045, format="%.6f", help="Ticari çelik için tipik değer: 0.000045 m")
    roughness = convert_value(roughness_input, len_unit, 'm')

if st.button("🚀 Hesaplamayı Başlat", use_container_width=True):
    re, flow_type, re_error = calculate_reynolds(density, velocity, diameter, viscosity)

    if re_error:
        st.error(f"Reynolds Hatası: {re_error}")
    else:
        st.subheader("📌 Sonuçlar")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            render_card("Reynolds Sayısı (Re)", f"{re:,.2f}")
            
            if flow_type == "Laminer":
                st.info("**Akış Tipi:** Laminer (Re < 2300)")
            elif flow_type == "Geçiş Bölgesi":
                st.warning("**Akış Tipi:** Geçiş (2300 ≤ Re ≤ 4000)")
            else:
                st.success("**Akış Tipi:** Türbülanslı (Re > 4000)")

        pressure_drop, fd, pd_error = calculate_pressure_drop(density, velocity, diameter, viscosity, length, roughness)
        if pd_error:
            st.error(f"Basınç Düşüşü Hatası: {pd_error}")
        else:
            with col_res2:
                render_card("Darcy Sürtünme Faktörü (fD)", f"{fd:.4f}")
                
                p_unit = units.get('P', 'Pa')
                pd_val = convert_value(pressure_drop, 'Pa', p_unit)
                render_card("Basınç Düşüşü (ΔP)", f"{pd_val:,.4f}", unit=p_unit)
