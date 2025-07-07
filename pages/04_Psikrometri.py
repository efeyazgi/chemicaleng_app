import streamlit as st
import pandas as pd
from src.calculators.psychrometrics_calculator import calculate_psychrometric_properties

st.set_page_config(page_title="Psikrometrik Hesaplayıcı", page_icon="🌬️")

st.title("🌬️ Psikrometrik Hesaplayıcı")
st.write("Nemli havanın termodinamik özelliklerini hesaplar.")

# Girdiler
P = st.number_input("Atmosfer Basıncı (Pa)", value=101325.0)
T_db_C = st.number_input("Kuru Termometre Sıcaklığı (°C)", value=25.0)

input_method = st.radio(
    "İkinci Bilinen Özelliği Seçin:",
    ("Bağıl Nem", "Yaş Termometre Sıcaklığı")
)

rh_input = None
T_wb_C_input = None

if input_method == "Bağıl Nem":
    rh_percent = st.number_input("Bağıl Nem (%)", min_value=0.0, max_value=100.0, value=50.0)
    rh_input = rh_percent / 100.0
else:
    T_wb_C_input = st.number_input("Yaş Termometre Sıcaklığı (°C)", value=20.0)

if st.button("Hesapla", use_container_width=True):
    try:
        # rh_input, 0-1 aralığında bir değerdir. Fonksiyon ise 0-100 aralığında bekliyor.
        rh_percent_arg = rh_input * 100 if rh_input is not None else None

        if T_wb_C_input is not None and T_wb_C_input > T_db_C:
            st.error("Yaş termometre sıcaklığı, kuru termometre sıcaklığından büyük olamaz.")
        else:
            df = calculate_psychrometric_properties(
                T_db_C=T_db_C, 
                P_Pa=P, 
                rh_percent=rh_percent_arg, 
                T_wb_C=T_wb_C_input
            )
            
            st.subheader("Sonuçlar")
            st.dataframe(df.style.format({'Değer': '{:.4f}'}), use_container_width=True)

    except Exception as e:
        st.error(f"Hesaplama sırasında bir hata oluştu: {e}")
