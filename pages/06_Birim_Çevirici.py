import streamlit as st
from src.calculators.unit_converter import UNIT_CATEGORIES, get_compatible_units, convert_units
import sys
import pint

st.set_page_config(page_title="Birim Çevirici", page_icon="📏")

# Başlık ve açıklama
st.title("📏 Genel Birim Çevirici")
st.markdown("Mühendislikte sık kullanılan uzunluk, basınç, sıcaklık gibi birimleri hızlıca dönüştürün.")

st.divider()

# 1. Nicelik türünü seç
quantity_type = st.selectbox("🔢 Çevirmek istediğiniz niceliği seçin:", list(UNIT_CATEGORIES.keys()))

# 2. Seçilen niceliğe göre birimleri al
units_raw = get_compatible_units(quantity_type)

# --- Türkçeleştirme sözlüğü ---
unit_translations = {
    # Uzunluk
    "meter": "Metre (m)",
    "centimeter": "Santimetre (cm)",
    "millimeter": "Milimetre (mm)",
    "kilometer": "Kilometre (km)",
    "micrometer": "Mikrometre (µm)",
    "nanometer": "Nanometre (nm)",
    "inch": "İnç (in)",
    "foot": "Foot (ft)",
    "yard": "Yarda (yd)",
    "mile": "Mil (mi)",
    "nautical_mile": "Deniz Mili (nmi)",
    "angstrom": "Angstrom (Å)",

    # Alan
    "meter**2": "Metrekare (m²)",
    "centimeter**2": "Santimetrekare (cm²)",
    "millimeter**2": "Milimetrekare (mm²)",
    "kilometer**2": "Kilometrekare (km²)",
    "inch**2": "İnç Kare (in²)",
    "foot**2": "Foot Kare (ft²)",
    "yard**2": "Yarda Kare (yd²)",
    "mile**2": "Mil Kare (mi²)",
    "acre": "Dönüm (acre)",
    "hectare": "Hektar (ha)",

    # Hacim
    "meter**3": "Metreküp (m³)",
    "centimeter**3": "Santimetreküp (cm³)",
    "millimeter**3": "Milimetreküp (mm³)",
    "inch**3": "İnç Küp (in³)",
    "foot**3": "Foot Küp (ft³)",
    "yard**3": "Yarda Küp (yd³)",
    "liter": "Litre (L)",
    "milliliter": "Mililitre (mL)",
    "microliter": "Mikrolitre (µL)",
    "gallon": "Galon (gal)",
    "quart": "Çeyrek Galon (qt)",
    "pint": "Pint (pt)",
    "cup": "Bardak (cup)",

    # Kütle
    "kilogram": "Kilogram (kg)",
    "gram": "Gram (g)",
    "milligram": "Miligram (mg)",
    "microgram": "Mikrogram (µg)",
    "ton": "Ton (ton)",
    "tonne": "Metrik Ton (tonne)",
    "pound": "Libre (lb)",
    "ounce": "Ons (oz)",
    "stone": "Taş (stone)",
    "carat": "Karat (ct)",

    # Sıcaklık
    "kelvin": "Kelvin (K)",
    "celsius": "Santigrat (°C)",
    "fahrenheit": "Fahrenheit (°F)",
    "rankine": "Rankine (°R)",

    # Basınç
    "pascal": "Pascal (Pa)",
    "kilopascal": "Kilopascal (kPa)",
    "megapascal": "Megapascal (MPa)",
    "bar": "Bar (bar)",
    "psi": "Psi (psi)",
    "atm": "Atmosfer (atm)",
    "torr": "Torr (torr)",
    "mmHg": "Milimetre Cıva (mmHg)",

    # Enerji
    "joule": "Joule (J)",
    "kilojoule": "Kilojoule (kJ)",
    "calorie": "Kalori (cal)",
    "kilocalorie": "Kilokalori (kcal)",
    "btu": "BTU (btu)",
    "erg": "Erg (erg)",

    # Güç
    "watt": "Watt (W)",
    "kilowatt": "Kilowatt (kW)",
    "megawatt": "Megawatt (MW)",
    "horsepower": "Beygir Gücü (hp)",

    # Zaman
    "second": "Saniye (s)",
    "minute": "Dakika (dk)",
    "hour": "Saat (h)",

    # Yoğunluk
    "kilogram/meter**3": "kg/m³",
    "gram/centimeter**3": "g/cm³",
    "pound/foot**3": "lb/ft³",

    # Hız
    "meter/second": "m/s",
    "kilometer/hour": "km/s",
    "foot/second": "ft/s",
    "mile/hour": "mil/s",
    "knot": "Knot (kn)",

    # Viskozite (Dinamik)
    "pascal*second": "Pascal.saniye (Pa·s)",
    "poise": "Poise (P)",
    "centipoise": "Sentipoise (cP)",
    "pound/(foot*second)": "lb/(ft·s)",
}

def translate(unit):
    return unit_translations.get(unit, unit)

# 3. Girdi ve çıktı birimlerini ve değeri al
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    value_to_convert = st.number_input("📥 Çevrilecek Değer:", value=1.0, format="%.4f")
with col2:
    from_unit = st.selectbox("🔹 Kaynak Birim:", units_raw, format_func=translate)
with col3:
    to_unit = st.selectbox("🔸 Hedef Birim:", units_raw, index=min(1, len(units_raw) - 1), format_func=translate)

# 4. Hesapla ve sonucu göster
if st.button("🚀 Çevir", use_container_width=True):
    if from_unit == to_unit:
        st.success(f"🔁 Sonuç: {value_to_convert} {translate(to_unit)}")
    else:
        result_val, error = convert_units(value_to_convert, from_unit, to_unit)
        if error:
            st.error(f"❌ Hata: {error}")
        else:
            st.success(f"✅ **{value_to_convert} {translate(from_unit)} → {result_val:.6g} {translate(to_unit)}**")
