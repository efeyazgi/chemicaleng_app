import streamlit as st
from src.calculators.unit_converter import UNIT_CATEGORIES, get_compatible_units, convert_units
import sys
import pint

st.set_page_config(page_title="Birim Çevirici", page_icon="📏")

print("[DEBUG] sys.executable:", sys.executable)
print("[DEBUG] pint location:", pint.__file__)

st.title("📏 Genel Birim Çevirici")

# 1. Nicelik türünü seç
quantity_type = st.selectbox("Çevirmek istediğiniz niceliği seçin:", list(UNIT_CATEGORIES.keys()))

# 2. Seçilen niceliğe göre birimleri al
units = get_compatible_units(quantity_type)

# 3. Girdi ve çıktı birimlerini ve değeri al
col1, col2, col3 = st.columns(3)
with col1:
    value_to_convert = st.number_input("Değer:", value=1.0, format="%.4f")
with col2:
    from_unit = st.selectbox("Kaynak Birim:", units)
with col3:
    to_unit = st.selectbox("Hedef Birim:", units, index=min(1, len(units)-1))

# 4. Hesapla ve sonucu göster
if st.button("Çevir", use_container_width=True):
    if from_unit == to_unit:
        st.success(f"**Sonuç:** {value_to_convert} {to_unit}")
    else:
        result_val, error = convert_units(value_to_convert, from_unit, to_unit)
        if error:
            st.error(f"Hata: {error}")
        else:
            st.success(f"**Sonuç:** {result_val:.6g} {to_unit}")
