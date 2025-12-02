
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from src.calculators.separation_calculator import calculate_mccabe_thiele, calculate_ponchon_savarit
from src.calculators.thermo_calculator import get_chemical_list
from src.utils.unit_manager import render_global_settings_sidebar, render_local_unit_override, convert_value, format_unit
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()

st.set_page_config(page_title="Ayırma İşlemleri", page_icon="⚗️", layout="wide")

render_header("Ayırma İşlemleri", "⚗️")
st.markdown("İkili karışımların distilasyon kolon hesaplamaları (McCabe-Thiele ve Ponchon-Savarit Yöntemleri).")
st.markdown("---")

# --- GİRİŞLER ---
col_left, col_right = st.columns([1, 2])

with col_left:
    # Global Ayarlar
    render_global_settings_sidebar()
    
    # Yerel Ayarlar
    unit_system, units = render_local_unit_override("separation")

    st.subheader("⚙️ Parametreler")
    
    # Yöntem Seçimi
    method = st.radio("Hesaplama Yöntemi:", ["McCabe-Thiele", "Ponchon-Savarit"], horizontal=True)
    
    # Akışkan Seçimi
    chem_list = get_chemical_list()
    chem_names_display = list(chem_list.values())
    chem_map = {v: k for k, v in chem_list.items()}
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        c1_disp = st.selectbox("Uçucu Bileşen (1)", chem_names_display, index=1) # Ethanol
    with col_c2:
        c2_disp = st.selectbox("Ağır Bileşen (2)", chem_names_display, index=0) # Water
        
    chem1 = chem_map[c1_disp]
    chem2 = chem_map[c2_disp]
    
    if chem1 == chem2:
        st.error("Lütfen iki farklı bileşen seçin.")
        st.stop()
        
    # İşletme Koşulları
    st.markdown("### 🌡️ İşletme Koşulları")
    
    p_unit = units.get('P', 'bar')
    P_input = st.number_input(f"Basınç ({format_unit(p_unit)})", value=1.01325, format="%.5f")
    # SI'ya çevir (Pa)
    P = convert_value(P_input, p_unit, 'Pa')
    
    st.markdown("### 📊 Konsantrasyonlar (Mol Kesri)")
    zF = st.slider("Besleme (zF)", 0.0, 1.0, 0.5)
    xD = st.slider("Distilat (xD)", 0.0, 1.0, 0.95)
    xB = st.slider("Dip Ürün (xB)", 0.0, 1.0, 0.05)
    
    st.markdown("### ⚙️ Kolon Ayarları")
    
    # Besleme Durumu Seçimi
    feed_condition_type = st.radio("Besleme Durumu:", ["q (Kalite) ile Belirle", "Sıcaklık ile Belirle"], horizontal=True)
    
    if feed_condition_type == "q (Kalite) ile Belirle":
        q = st.number_input("Besleme Kalitesi (q)", value=1.0, help="q=1: Doygun Sıvı, q=0: Doygun Buhar, q>1: Alt Soğutulmuş Sıvı")
    else:
        # Varsayılan sıcaklık tahmini (Kaynama noktası civarı)
        try:
            from thermo import Chemical
            T_boil_K = Chemical(chem1, P=P).Tb
        except:
            T_boil_K = 350.0
        
        t_unit = units.get('T', 'K')
        # Varsayılan değeri hedef birime çevir
        T_boil_val = convert_value(T_boil_K, 'K', t_unit)
            
        T_feed_input = st.number_input(f"Besleme Sıcaklığı ({format_unit(t_unit)})", value=float(T_boil_val), format="%.2f")
        # SI'ya çevir (K)
        T_feed = convert_value(T_feed_input, t_unit, 'K')
        q = None # Daha sonra hesaplanacak

    R = st.number_input("Geri Akış Oranı (R)", value=1.5, min_value=0.0)
    
    calc_btn = st.button("🚀 Hesapla", type="primary", use_container_width=True)

# --- SONUÇLAR ---
with col_right:
    if calc_btn:
        with st.spinner("Hesaplanıyor... (Termodinamik veriler çekiliyor)"):
            try:
                # Eğer sıcaklık seçildiyse q'yu hesapla
                if feed_condition_type == "Sıcaklık ile Belirle":
                    from src.calculators.separation_calculator import calculate_q_from_T
                    q = calculate_q_from_T(chem1, chem2, P, zF, T_feed)
                    st.info(f"ℹ️ Hesaplanan Besleme Kalitesi (q): **{q:.4f}**")

                if method == "McCabe-Thiele":
                    vle_df, q_df, rect_df, strip_df, trays, steps = calculate_mccabe_thiele(
                        chem1, chem2, P, zF, xD, xB, q, R
                    )
                    
                    st.success(f"✅ Teorik Raf Sayısı: **{trays}**")
                    
                    # Grafik
                    base = alt.Chart(pd.DataFrame({'x': [0, 1], 'y': [0, 1]})).mark_rule(color='lightgray', strokeDash=[5, 5]).encode(x='x', y='y')
                    
                    vle_chart = alt.Chart(vle_df).mark_line(color='#1f77b4', strokeWidth=3).encode(
                        x=alt.X('x', title=f'Sıvı Mol Kesri ({chem1})'),
                        y=alt.Y('y', title=f'Buhar Mol Kesri ({chem1})'),
                        tooltip=['x', 'y', 'T']
                    )
                    
                    rect_chart = alt.Chart(rect_df).mark_line(color='#2ca02c', strokeWidth=2).encode(x='x', y='y') # Green
                    strip_chart = alt.Chart(strip_df).mark_line(color='#d62728', strokeWidth=2).encode(x='x', y='y') # Red
                    q_chart = alt.Chart(q_df).mark_line(color='#9467bd', strokeDash=[5, 5]).encode(x='x', y='y') # Purple
                    
                    steps_df = pd.DataFrame(steps, columns=['x', 'y'])
                    steps_chart = alt.Chart(steps_df).mark_line(color='black', strokeWidth=1.5, interpolate='step-after').encode(x='x', y='y')
                    
                    chart = (base + vle_chart + rect_chart + strip_chart + q_chart + steps_chart).properties(
                        title="McCabe-Thiele Diyagramı",
                        height=600
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                else: # Ponchon-Savarit
                    df, points, trays, steps = calculate_ponchon_savarit(
                        chem1, chem2, P, zF, xD, xB, q, R
                    )
                    
                    if trays == float('inf'):
                         st.error("❌ Ayırma bu koşullarda mümkün değil veya çok zor (R < R_min veya Pinch Noktası). Lütfen Geri Akış Oranını (R) artırın.")
                    else:
                        st.success(f"✅ Teorik Raf Sayısı: **{trays}**")
                        render_card("Teorik Raf Sayısı", str(trays), unit="Adet")
                    
                    # H-x-y Diyagramı
                    # Entalpi birimi
                    energy_unit = units.get('Energy', 'J')
                    # Ponchon-Savarit J/mol döner
                    # Hedef birim: energy_unit / mol (e.g. kJ/mol)
                    # Ancak energy_unit sadece J, kJ, Btu vs.
                    # Biz J/mol -> energy_unit/mol çevireceğiz.
                    
                    # Basitçe J -> energy_unit çevirimi yapıp grafikte gösterebiliriz, çünkü payda mol sabit.
                    # Fakat kullanıcı J/kg gibi bir şey beklemiyor, molar entalpi bekliyor.
                    # Unit manager'da MolarEnergy yok, ama Energy var.
                    # J -> kJ çevirimi yeterli olur.
                    
                    # df['HL'] ve df['HV'] J/mol cinsinden.
                    # Bunları hedef birime çevirelim.
                    
                    target_h_unit = f"{energy_unit}/mol"
                    # Pint ile J/mol -> target_h_unit
                    
                    # Veriyi kopyalayalım
                    df_plot = df.copy()
                    df_plot['HL'] = [convert_value(x, 'J/mol', target_h_unit) for x in df['HL']]
                    df_plot['HV'] = [convert_value(x, 'J/mol', target_h_unit) for x in df['HV']]
                    
                    # Noktaları da çevirelim
                    points_plot = {}
                    for k, v in points.items():
                         points_plot[k] = (v[0], convert_value(v[1], 'J/mol', target_h_unit))
                    
                    h_axis_title = f"Entalpi ({format_unit(energy_unit)}/mol)"

                    # Doygun Sıvı Eğrisi
                    liq_chart = alt.Chart(df_plot).mark_line(color='#1f77b4', strokeWidth=3).encode(
                        x=alt.X('x', title=f'Mol Kesri ({chem1})'),
                        y=alt.Y('HL', title=h_axis_title),
                        tooltip=['x', 'HL', 'T']
                    )
                    
                    # Doygun Buhar Eğrisi
                    vap_chart = alt.Chart(df_plot).mark_line(color='#d62728', strokeWidth=3).encode(
                        x=alt.X('y', title=f'Mol Kesri ({chem1})'),
                        y=alt.Y('HV', title=h_axis_title),
                        tooltip=['y', 'HV', 'T']
                    )
                    
                    # Delta Noktaları ve F
                    pts_data = pd.DataFrame([
                        {'x': points_plot['F'][0], 'H': points_plot['F'][1], 'Label': 'F'},
                        {'x': points_plot['D'][0], 'H': points_plot['D'][1], 'Label': 'D'},
                        {'x': points_plot['B'][0], 'H': points_plot['B'][1], 'Label': 'B'},
                        {'x': points_plot['Delta_D'][0], 'H': points_plot['Delta_D'][1], 'Label': 'ΔD'},
                        {'x': points_plot['Delta_B'][0], 'H': points_plot['Delta_B'][1], 'Label': 'ΔB'},
                    ])
                    
                    pts_chart = alt.Chart(pts_data).mark_point(size=100, filled=True, color='black').encode(
                        x='x', y='H', tooltip=['Label', 'x', 'H']
                    )
                    
                    text_chart = pts_chart.mark_text(align='left', dx=5, dy=-5).encode(text='Label')
                    
                    # Tie-lines (Denge Bağları) ve Operasyon Çizgileri
                    # Steps listesi: (x, HL) -> (y, HV) -> (x_next, HL_next) ...
                    # Bunları çizmek için segmentler oluşturmalıyız.
                    
                    lines_data = []
                    for i in range(len(steps)-1):
                        p1 = steps[i]
                        p2 = steps[i+1]
                        # Koordinatları çevir
                        h1 = convert_value(p1[1], 'J/mol', target_h_unit)
                        h2 = convert_value(p2[1], 'J/mol', target_h_unit)
                        lines_data.append({'x1': p1[0], 'H1': h1, 'x2': p2[0], 'H2': h2, 'Type': 'Tie' if i%2==0 else 'Op'})
                        
                    lines_df = pd.DataFrame(lines_data)
                    if not lines_df.empty:
                        lines_chart = alt.Chart(lines_df).mark_line(strokeWidth=1).encode(
                            x='x1', y='H1', x2='x2', y2='H2', 
                            color=alt.Color('Type', scale=alt.Scale(domain=['Tie', 'Op'], range=['green', 'orange']))
                        )
                        chart = (liq_chart + vap_chart + pts_chart + text_chart + lines_chart).properties(
                            title="Ponchon-Savarit Diyagramı (H-x-y)",
                            height=600
                        ).interactive()
                    else:
                        chart = (liq_chart + vap_chart + pts_chart + text_chart).properties(height=600).interactive()

                    st.altair_chart(chart, use_container_width=True)
                    
                    # VLE Grafiği de gösterelim (Referans için)
                    with st.expander("VLE Diyagramı"):
                        vle_chart = alt.Chart(df).mark_line().encode(x='x', y='y').properties(title="x-y Diyagramı")
                        st.altair_chart(vle_chart, use_container_width=True)

            except Exception as e:
                st.error(f"Hesaplama hatası: {e}")
                # st.exception(e) # Debug için açılabilir
    else:
        st.info("👈 Parametreleri ayarlayıp 'Hesapla' butonuna basın.")
