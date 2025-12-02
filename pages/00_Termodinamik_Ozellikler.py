import streamlit as st
import pandas as pd
import altair as alt
from src.calculators.thermo_calculator import calculate_properties, generate_plot_data, get_chemical_list
from src.utils.unit_manager import render_global_settings_sidebar, render_local_unit_override
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()

st.set_page_config(page_title="Termodinamik Özellikler", page_icon="🌡️", layout="wide")

# Başlık
render_header("Termodinamik Özellikler", "🌡️")
st.markdown("Saf maddelerin sıcaklık ve basınca bağlı termodinamik ve taşıma özelliklerini hesaplayın.")
st.markdown("---")

# Alt indis fonksiyonu
def to_subscript(s):
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return s.translate(subscript_map)

# --- GİRİŞ ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("⚙️ Ayarlar")
    
    # Global Ayarlar Sidebar
    render_global_settings_sidebar()

    # Yerel Ayarlar
    unit_system, effective_units = render_local_unit_override("thermo")
    
    # Calculator için uyumluluk (Metric -> Metric (CGS))
    calc_unit_system = unit_system
    if unit_system == "Metric":
        calc_unit_system = "Metric (CGS)"
    
    # Manuel birim haritalama (Calculator beklediği format -> Unit Manager formatı)
    # Calculator keys: rho, mu, Cp, Psat, sigma, k, Tb, Tm
    # Unit Manager keys: Density, Viscosity, Cp, P, SurfaceTension, ThermalCond, T
    
    mapped_manual_units = {}
    if unit_system == "Manual":
        mapped_manual_units = {
            'rho': effective_units.get('Density'),
            'mu': effective_units.get('Viscosity'),
            'Cp': effective_units.get('Cp'),
            'Psat': effective_units.get('P'),
            'sigma': effective_units.get('SurfaceTension'),
            'k': effective_units.get('ThermalCond'),
            'Tb': effective_units.get('T'),
            'Tm': effective_units.get('T'),
            'T': effective_units.get('T'),
            'P': effective_units.get('P')
        }

    # Akışkan Seçimi
    st.markdown("Akışkan isimleri için [Thermo Kütüphanesi Dokümantasyonu](https://thermo.readthedocs.io/thermo.chemical.html) sayfasını inceleyebilirsiniz.")
    
    input_method = st.radio("Giriş Yöntemi:", ["Listeden Seç", "Manuel İsim Gir"], horizontal=True)

    chem_list = get_chemical_list()
    chem_names_display = list(chem_list.values())
    chem_map = {v: k for k, v in chem_list.items()}

    if input_method == "Listeden Seç":
        selected_chem_display = st.selectbox("Akışkan Seç:", options=chem_names_display, index=0)
        chemical_name = chem_map[selected_chem_display]
    else:
        manual_chemical = st.text_input("İngilizce İsim Girin:", "", placeholder="Örn: toluene, acetone, hexane")
        chemical_name = manual_chemical.strip()

    # Sıcaklık ve Basınç Girişleri
    st.markdown("### 🌡️ Durum")
    
    # Varsayılanlar ve Etiketler
    # Varsayılanlar ve Etiketler
    t_unit_label = effective_units['T']
    p_unit_label = effective_units['P']
    
    t_label = f"Sıcaklık ({t_unit_label})"
    p_label = f"Basınç ({p_unit_label})"
    
    # Varsayılan değerler (Birim sistemine göre mantıklı başlangıçlar)
    if unit_system == "Metric":
        t_val, p_val = 25.0, 1.0
    elif unit_system == "English":
        t_val, p_val = 77.0, 14.7
    else: # SI or Manual (default to SI-like numbers if manual doesn't imply otherwise, but let's stick to SI defaults for manual to be safe or check unit)
        # Basitlik için Manual ise SI varsayalım, kullanıcı değiştirsin
        t_val, p_val = 300.0, 101325.0

    t_input = st.number_input(t_label, value=t_val, format="%.2f")
    p_input = st.number_input(p_label, value=p_val, format="%.4f")

    # Özellik Seçimi
    st.markdown("### 📝 Özellikler")
    property_options = {
        "Yoğunluk (rho)": "rho", "Viskozite (mu)": "mu", "Isı Kapasitesi (Cp)": "Cp",
        "Buhar Basıncı (Psat)": "Psat", "Yüzey Gerilimi (sigma)": "sigma",
        "Isıl İletkenlik (k)": "k", "Kaynama Noktası (Tb)": "Tb", "Donma Noktası (Tm)": "Tm"
    }
    
    selected_properties = st.multiselect(
        "Hesaplanacaklar:",
        options=list(property_options.keys()),
        default=["Yoğunluk (rho)", "Viskozite (mu)", "Isı Kapasitesi (Cp)"]
    )

    # Manuel Çıktı Birimleri (Artık Unit Manager ile yönetiliyor, burada sadece bilgi verebiliriz veya gizleyebiliriz)
    if unit_system == "Manual" and selected_properties:
        st.info(f"Seçili Manuel Birimler: {mapped_manual_units}")

    calculate_btn = st.button("🚀 Hesapla", type="primary", use_container_width=True)

# --- SONUÇLAR ---
# --- SONUÇLAR ---
with col_right:
    if calculate_btn:
        if not chemical_name:
            st.warning("Lütfen bir akışkan seçin veya girin.")
        elif not selected_properties:
            st.warning("En az bir özellik seçmelisiniz.")
        else:
            with st.spinner("Hesaplanıyor..."):
                try:
                    df, formula = calculate_properties(
                        chemical_name, t_input, p_input,
                        calc_unit_system, selected_properties, mapped_manual_units
                    )
                    
                    # Hata kontrolü
                    if not df.empty and "Hata" in df.iloc[0].values:
                        st.error(df.iloc[0]["Değer"])
                        st.session_state.thermo_results = None
                    else:
                        # Sonuçları session_state'e kaydet
                        st.session_state.thermo_results = {
                            'df': df,
                            'formula': formula,
                            'chemical_name': chemical_name,
                            'unit_system': calc_unit_system,
                            'p_input': p_input,
                            't_input': t_input,
                            'manual_units': mapped_manual_units,
                            'selected_properties': selected_properties
                        }
                except Exception as e:
                    st.error(f"Beklenmeyen bir hata oluştu: {e}")
                    st.session_state.thermo_results = None

    # Sonuçları Göster (Session State'den)
    if st.session_state.get('thermo_results'):
        res = st.session_state.thermo_results
        df = res['df']
        formula = res['formula']
        chem_name = res['chemical_name']
        
        # Başlık
        chem_title = chem_name.title()
        # Listeden seçildiyse Türkçe ismini bulmaya çalışalım (basitçe)
        # Ama burada karmaşıklık yaratmamak için kaydedilen ismi kullanıyoruz.
        
        title = f"🧪 {chem_title} ({to_subscript(formula)})" if formula else f"🧪 {chem_title}"
        st.subheader(title)
        
        # Sonuçları Kartlar Halinde Göster
        res_cols = st.columns(3)
        for idx, row in df.iterrows():
            with res_cols[idx % 3]:
                render_card(
                    title=row['Özellik'],
                    value=str(row['Değer']),
                    unit=row['Birim']
                )

        # Tablo ve İndirme
        with st.expander("📋 Detaylı Tablo", expanded=False):
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 CSV İndir", df.to_csv(index=False), "termo_sonuclar.csv")

        # Grafik Bölümü
        st.markdown("### 📊 Grafik Analizi")
        
        # Grafik için uygun özellikler (Tb ve Tm hariç)
        plottable_props = [p for p in res['selected_properties'] if property_options[p] not in ['Tb', 'Tm']]
        
        if plottable_props:
            prop_to_plot = st.selectbox("Grafik Özelliği:", plottable_props)
            
            t_range_col1, t_range_col2 = st.columns(2)
            # Varsayılan aralık: Giriş sıcaklığının +/- 50 birim çevresi
            t_center = res['t_input']
            t_min_plot = t_range_col1.number_input("Min T", value=t_center - 50)
            t_max_plot = t_range_col2.number_input("Maks T", value=t_center + 50)
            
            if st.button("📈 Grafiği Güncelle"):
                with st.spinner("Grafik oluşturuluyor..."):
                    plot_df = generate_plot_data(
                        res['chemical_name'], 
                        res['p_input'], 
                        res['unit_system'],
                        property_options[prop_to_plot], 
                        t_min_plot, 
                        t_max_plot,
                        res['manual_units']
                    )
                    
                    if not plot_df.empty:
                        chart = alt.Chart(plot_df).mark_line(point=True).encode(
                            x=alt.X('Sıcaklık', title=f'Sıcaklık'),
                            y=alt.Y('Özellik', title=prop_to_plot),
                            tooltip=['Sıcaklık', 'Özellik']
                        ).interactive()
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning("Bu aralıkta veri üretilemedi (Sıcaklık aralığını veya birimleri kontrol edin).")
        else:
            st.info("Grafik çizilebilecek bir özellik seçilmedi.")
    
    elif not calculate_btn:
        st.info("👈 Sol panelden parametreleri seçip 'Hesapla' butonuna basın.")
