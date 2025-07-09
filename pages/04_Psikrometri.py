import streamlit as st
import pandas as pd
from src.calculators.psychrometrics_calculator import (
    calculate_psychrometric_properties,
    generate_psychrometric_chart
)

st.set_page_config(page_title="Psikrometrik Hesaplayıcı", page_icon="🌬️")
st.title("🌬️ Psikrometrik Hesaplayıcı")
st.markdown("Bu modül, nemli havanın termodinamik özelliklerini (entalpi, nem oranı, çiğ noktası vs.) hesaplamanıza ve psikrometrik diyagram üretmenize yardımcı olur.")

st.divider()

# --- GİRİŞ ---
with st.expander("🧮 Giriş Parametreleri", expanded=True):
    P = st.number_input("Atmosfer Basıncı (Pa)", value=101325.0)
    T_db_C = st.number_input("Kuru Termometre Sıcaklığı (°C)", value=25.0)

    method = st.radio("İkinci Bilinen Özellik:", ("Bağıl Nem (%)", "Yaş Termometre Sıcaklığı (°C)"))

    if method == "Bağıl Nem (%)":
        rh = st.slider("Bağıl Nem (%)", 0, 100, 50)
        T_wb = None
    else:
        rh = None
        T_wb = st.number_input("Yaş Termometre Sıcaklığı (°C)", value=20.0)

    if st.button("🔎 Hesapla"):
        try:
            props = calculate_psychrometric_properties(T_db_C, P, rh, T_wb)
            st.session_state.psychro_props = props
            st.session_state.psychro_P = P
            st.session_state.psychro_T = T_db_C
        except Exception as e:
            st.error(f"Hesaplama sırasında hata oluştu: {e}")
            st.session_state.psychro_props = None

# --- SONUÇLARI GÖSTER (Varsa) ---
props = st.session_state.get("psychro_props")
if props:
    st.subheader("📌 Hesaplanan Özellikler")

    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Yaş Termometre (°C)", f"{props['T_wb (°C)']:.2f}")
    col2.metric("💧 Çiğ Noktası (°C)", f"{props['T_dp (°C)']:.2f}")
    col3.metric("🔁 Bağıl Nem (%)", f"{props['RH (%)']:.1f}")

    col4, col5, col6 = st.columns(3)
    col4.metric("⚙️ Nem Oranı (kg/kg)", f"{props['w (kg_water/kg_dry)']:.5f}")
    col5.metric("🔥 Entalpi (kJ/kg dry)", f"{props['h (kJ/kg_dry)']:.2f}")
    col6.metric("📦 Özgül Hacim (m³/kg)", f"{props['v (m³/kg_dry)']:.4f}")

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
