import streamlit as st
import pandas as pd
import altair as alt
from src.calculators.thermo_calculator import calculate_properties, generate_plot_data

st.set_page_config(page_title="Termodinamik Özellikler", page_icon="🌡️")

# Alt indis fonksiyonu
def to_subscript(s):
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return s.translate(subscript_map)

st.title("🌡️ Termodinamik Özellikler")

# --- Saf Madde Hesaplayıcısı ---
with st.expander("Saf Madde Özellikleri", expanded=True):
    st.write(
        "Bu bölüm, saf maddelerin sıcaklık ve basınca bağlı "
        "termodinamik ve taşıma özelliklerini hesaplar."
    )

    # Birim seçimi
    unit_system = st.radio(
        "Birim Sistemi Profili:", 
        ("SI", "Metric (CGS)", "English"), 
        horizontal=True,
        help="SI (K, Pa), Metric (C, bar), English (°F, psia)",
        key="pure_comp_units"
    )

    # Sık kullanılan akışkanlar listesi
    common_chemicals = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]

    selected_chemical = st.selectbox(
        "Sık kullanılan akışkanlardan seç veya aşağıya manuel gir:",
        options=common_chemicals,
        key="pure_comp_select"
    )

    manual_chemical = st.text_input("Akışkan Adı (manuel giriyorsan):", "", key="pure_comp_manual")
    chemical_name = manual_chemical.strip() if manual_chemical else selected_chemical

    # Birimlere göre dinamik değerler
    if unit_system == "SI":
        temp_label, press_label = "Sıcaklık (K)", "Basınç (Pa)"
        temp_default, press_default = 300.0, 101325.0
    elif unit_system == "Metric (CGS)":
        temp_label, press_label = "Sıcaklık (°C)", "Basınç (bar)"
        temp_default, press_default = 25.0, 1.0
    elif unit_system == "English":
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
        "Hesaplanacak Özellikleri Seç:",
        options=list(property_options.keys()),
        default=["Yoğunluk (rho)", "Viskozite (mu)", "Isı Kapasitesi (Cp)"],
        key="pure_props"
    )

    if 'thermo_results_df' not in st.session_state:
        st.session_state.thermo_results_df = None
    if 'thermo_formula' not in st.session_state:
        st.session_state.thermo_formula = None

    if st.button("Hesapla", use_container_width=True, key="pure_calc"):
        if not chemical_name:
            st.warning("Lütfen bir akışkan adı girin.")
        elif not selected_properties:
            st.warning("Lütfen en az bir özellik seçin.")
        else:
            try:
                df, formula = calculate_properties(
                    chemical_name, temperature_input, pressure_input,
                    unit_system, selected_properties
                )
                st.session_state.thermo_results_df = df
                st.session_state.thermo_formula = formula
            except Exception as e:
                st.session_state.thermo_results_df = None
                st.session_state.thermo_formula = None
                st.error(f"Hata oluştu: {e}")

    if st.session_state.thermo_results_df is not None:
        df = st.session_state.thermo_results_df
        st.session_state.thermo_chemical_name = chemical_name 
        if st.session_state.thermo_formula:
            formula_display = to_subscript(st.session_state.thermo_formula)
            st.subheader(f"🧪 {st.session_state.thermo_chemical_name.title()} ({formula_display}) için Sonuçlar")
        else:
            st.subheader(f"🧪 {st.session_state.thermo_chemical_name.title()} için Sonuçlar")
        st.dataframe(df, use_container_width=True)
        
        # Grafik Çizim
        st.subheader("📊 Grafik Çizimi")
        plottable_properties = df[pd.to_numeric(df['Değer'], errors='coerce').notna()]['Özellik'].tolist()
        if not plottable_properties:
            st.info("Grafik çizmek için uygun bir özellik hesaplanmadı.")
        else:
            prop_to_plot_name = st.selectbox(
                "Grafiği çizilecek özelliği seçin:", options=plottable_properties,
                key=f"plot_select_{chemical_name}"
            )
            t_unit = "(K)" if unit_system == "SI" else "(°C)"
            c1, c2 = st.columns(2)
            temp_min_plot = c1.number_input(f"Min. Sıcaklık {t_unit}", value=float(temperature_input - 50), key="t_min")
            temp_max_plot = c2.number_input(f"Maks. Sıcaklık {t_unit}", value=float(temperature_input + 50), key="t_max")
            if st.button("Grafik Çiz", key="pure_plot"):
                if temp_min_plot >= temp_max_plot:
                    st.error("Minimum sıcaklık, maksimum sıcaklıktan küçük olmalıdır.")
                else:
                    with st.spinner("Grafik oluşturuluyor..."):
                        plot_df = generate_plot_data(
                            chemical_name, pressure_input, unit_system,
                            property_options[prop_to_plot_name], temp_min_plot, temp_max_plot
                        )
                        if not plot_df.empty:
                            chart = alt.Chart(plot_df).mark_line().encode(
                                x=alt.X('Sıcaklık', title=f'Sıcaklık {t_unit}'),
                                y=alt.Y('Özellik', title=f'{prop_to_plot_name}'),
                                tooltip=['Sıcaklık', 'Özellik']
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.warning("Bu aralıkta grafik için veri üretilemedi.")
