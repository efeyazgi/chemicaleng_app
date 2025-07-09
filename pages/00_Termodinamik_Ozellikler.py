import streamlit as st
import pandas as pd
import altair as alt
from src.calculators.thermo_calculator import calculate_properties, generate_plot_data

st.set_page_config(page_title="Termodinamik Özellikler", page_icon="🌡️")

# Başlık
st.title("🌡️ Termodinamik Özellikler")
st.markdown("Bu bölümde saf maddelerin sıcaklık ve basınca bağlı termodinamik ve taşıma özelliklerini hesaplayabilirsiniz.")

# Alt indis fonksiyonu
def to_subscript(s):
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return s.translate(subscript_map)

# --- GİRİŞ ---
with st.expander("🔍 Girdi Parametreleri", expanded=True):

    unit_system = st.radio(
        "Birim Sistemi:", 
        ("SI", "Metric (CGS)", "English"), 
        horizontal=True,
        help="SI (K, Pa), Metric (°C, bar), English (°F, psia)",
        key="pure_comp_units"
    )

    common_chemicals = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]

    selected_chemical = st.selectbox("Akışkan Seç:", options=common_chemicals, key="pure_comp_select")
    manual_chemical = st.text_input("Manuel Giriş (İsteğe Bağlı):", "", key="pure_comp_manual")
    chemical_name = manual_chemical.strip() if manual_chemical else selected_chemical

    # Birimlere göre varsayılanlar
    if unit_system == "SI":
        temp_label, press_label = "Sıcaklık (K)", "Basınç (Pa)"
        temp_default, press_default = 300.0, 101325.0
    elif unit_system == "Metric (CGS)":
        temp_label, press_label = "Sıcaklık (°C)", "Basınç (bar)"
        temp_default, press_default = 25.0, 1.0
    else:
        temp_label, press_label = "Sıcaklık (°F)", "Basınç (psia)"
        temp_default, press_default = 77.0, 14.7

    col1, col2 = st.columns(2)
    with col1:
        temperature_input = st.number_input(temp_label, value=temp_default, key="pure_temp")
    with col2:
        pressure_input = st.number_input(press_label, value=press_default, key="pure_press")

    property_options = {
        "Yoğunluk (rho)": "rho", "Viskozite (mu)": "mu", "Isı Kapasitesi (Cp)": "Cp",
        "Buhar Basıncı (Psat)": "Psat", "Yüzey Gerilimi (sigma)": "sigma",
        "Isıl İletkenlik (k)": "k", "Kaynama Noktası (Tb)": "Tb", "Donma Noktası (Tm)": "Tm"
    }

    selected_properties = st.multiselect(
        "Hesaplanacak Özellikler:",
        options=list(property_options.keys()),
        default=["Yoğunluk (rho)", "Viskozite (mu)", "Isı Kapasitesi (Cp)"],
        key="pure_props"
    )

    if st.button("🧮 Hesapla", use_container_width=True):
        if not chemical_name:
            st.warning("Lütfen bir akışkan adı girin.")
        elif not selected_properties:
            st.warning("En az bir özellik seçmelisiniz.")
        else:
            try:
                df, formula = calculate_properties(
                    chemical_name, temperature_input, pressure_input,
                    unit_system, selected_properties
                )
                st.session_state.thermo_results_df = df
                st.session_state.thermo_formula = formula
                st.session_state.thermo_chemical_name = chemical_name
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
                st.session_state.thermo_results_df = None

# --- SONUÇLAR ---
if st.session_state.get("thermo_results_df") is not None:
    df = st.session_state.thermo_results_df
    chem = st.session_state.thermo_chemical_name.title()
    formula = st.session_state.get("thermo_formula")
    title = f"🧪 {chem} ({to_subscript(formula)}) için Sonuçlar" if formula else f"🧪 {chem} için Sonuçlar"
    
    st.subheader(title)
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Sonuçları İndir (CSV)", data=df.to_csv(index=False), file_name="termodinamik_sonuclar.csv")

    # --- Grafik ---
    st.markdown("### 📊 Özellik Grafiği")
    plottable_properties = df[pd.to_numeric(df['Değer'], errors='coerce').notna()]['Özellik'].tolist()
    if not plottable_properties:
        st.info("Grafik çizmek için uygun bir özellik hesaplanmadı.")
    else:
        prop_to_plot_name = st.selectbox("Grafiği çizilecek özellik:", options=plottable_properties)
        t_unit = "(K)" if unit_system == "SI" else "(°C)"
        col1, col2 = st.columns(2)
        temp_min_plot = col1.number_input(f"Min. Sıcaklık {t_unit}", value=temperature_input - 50)
        temp_max_plot = col2.number_input(f"Maks. Sıcaklık {t_unit}", value=temperature_input + 50)

        if st.button("📈 Grafik Çiz", key="plot_btn"):
            if temp_min_plot >= temp_max_plot:
                st.error("Minimum sıcaklık, maksimum sıcaklıktan küçük olmalıdır.")
            else:
                plot_df = generate_plot_data(
                    chemical_name, pressure_input, unit_system,
                    property_options[prop_to_plot_name], temp_min_plot, temp_max_plot
                )
                if not plot_df.empty:
                    chart = alt.Chart(plot_df).mark_line().encode(
                        x=alt.X('Sıcaklık', title=f'Sıcaklık {t_unit}'),
                        y=alt.Y('Özellik', title=prop_to_plot_name),
                        tooltip=['Sıcaklık', 'Özellik']
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning("Bu aralıkta grafik için veri üretilemedi.")
