import streamlit as st
import pandas as pd
from src.calculators.unit_converter import UNIT_CATEGORIES, UNIT_DISPLAY_NAMES, convert_units

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Birim Çevirici",
    page_icon="📏",
    layout="wide"
)

# Başlık ve Açıklama
st.title("📏 Genel Birim Çevirici")
st.markdown("---")

# Kategori Seçimi
categories = list(UNIT_CATEGORIES.keys())
selected_category = st.selectbox("📂 Kategori Seçin", categories, index=0)

# Seçilen kategoriye ait birimler
units = UNIT_CATEGORIES[selected_category]

# Girdi Alanı
col1, col2 = st.columns([1, 1])

with col1:
    input_value = st.number_input("Değer Girin", value=1.0, format="%.4f")

with col2:
    # Birimlerin Türkçe isimlerini gösteren selectbox
    from_unit = st.selectbox(
        "Giriş Birimi", 
        units, 
        index=0,
        format_func=lambda x: UNIT_DISPLAY_NAMES.get(x, x)
    )

st.markdown("---")

# Sonuçları Hesapla ve Göster
st.subheader("🔄 Çevrim Sonuçları")

if st.button("🚀 Çevir", type="primary", use_container_width=True):
    results_data = []
    for target_unit in units:
        val, error = convert_units(input_value, from_unit, target_unit)
        if error:
            continue
        
        # Türkçe ismi al
        display_name = UNIT_DISPLAY_NAMES.get(target_unit, target_unit)
        results_data.append({"Birim": display_name, "Değer": val})

    # Sonuçları güzel bir gridde gösterelim
    cols = st.columns(3)
    for i, item in enumerate(results_data):
        val = item['Değer']
        unit = item['Birim']
        
        # Biçimlendirme
        if abs(val) < 1e-4 or abs(val) > 1e5:
            disp_val = f"{val:.5e}"
        else:
            disp_val = f"{val:.5f}"
            
        with cols[i % 3]:
            st.container(border=True).metric(label=unit, value=disp_val)
