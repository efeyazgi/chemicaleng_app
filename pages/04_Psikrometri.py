import streamlit as st
import pandas as pd
from src.calculators.psychrometrics_calculator import (
    calculate_psychrometric_properties,
    generate_psychrometric_chart
)

st.set_page_config(page_title="Psikrometrik Hesaplayıcı", page_icon="🌬️")
st.title("🌬️ Psikrometrik Hesaplayıcı")

# Girdiler
P = st.number_input("Atmosfer Basıncı (Pa)", value=101325.0)
T_db_C = st.number_input("Kuru Termometre Sıcaklığı (°C)", value=25.0)
method = st.radio("İkinci Bilinen Özelliği Seçin:", ("Bağıl Nem","Yaş Termometre Sıcaklığı"))
if method=="Bağıl Nem":
    rh = st.slider("Bağıl Nem (%)", 0,100,50)
    T_wb = None
else:
    rh = None
    T_wb = st.number_input("Yaş Termometre Sıcaklığı (°C)", value=20.0)

if st.button("Hesapla"):
    try:
        props = calculate_psychrometric_properties(T_db_C,P, rh, T_wb)
        df = pd.DataFrame(list(props.items()), columns=["Özellik","Değer"] )
        st.subheader("Sonuçlar")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(e)

st.markdown("---")
if st.button("Psikrometrik Diyagramı Göster"):
    fig = generate_psychrometric_chart(P, T_min=0, T_max=50)
    st.pyplot(fig)