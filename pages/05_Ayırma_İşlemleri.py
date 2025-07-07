import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Ayırma İşlemleri", page_icon="⚗️")

st.title("⚗️ Ayırma İşlemleri")

st.info("Bu modül, ikili karışımlar için McCabe-Thiele metodunu kullanarak distilasyon kolonlarını analiz eder.")
st.warning("**Not:** Bu özellik deneyseldir. Temel alınan VLE hesaplaması, bazı sistemler veya koşullar için sayısal olarak kararlı sonuçlar üretemeyebilir.")

with st.form(key="mccabe_thiele_form"):
    st.subheader("Sistem ve Besleme Bilgileri")
    
    # Sık kullanılan akışkanlar listesi (Termodinamik sayfasından kopyalandı)
    common_chemicals = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        chem1 = st.selectbox("Hafif Bileşen:", options=common_chemicals, index=3) # Benzene
    with col2:
        chem2 = st.selectbox("Ağır Bileşen:", options=common_chemicals, index=4) # Toluene

    P = st.number_input("Kolon Basıncı (Pa)", value=101325.0, help="VLE verileri bu basınçta hesaplanacaktır.")

    st.subheader("Kompozisyon ve Akış Koşulları")
    col1, col2, col3 = st.columns(3)
    with col1:
        zF = st.number_input("Besleme Komp. (zF)", min_value=0.01, max_value=0.99, value=0.5, format="%.2f")
    with col2:
        xD = st.number_input("Distilat Komp. (xD)", min_value=0.01, max_value=0.99, value=0.95, format="%.2f")
    with col3:
        xB = st.number_input("Dip Ürün Komp. (xB)", min_value=0.01, max_value=0.99, value=0.05, format="%.2f")

    col1, col2 = st.columns(2)
    with col1:
        q = st.number_input("Besleme Kalitesi (q)", value=1.0, help="Doymuş sıvı için q=1, doymuş buhar için q=0")
    with col2:
        R = st.number_input("Reflüks Oranı (R)", min_value=0.0, value=2.5)

    submit_button = st.form_submit_button(label="Analizi Başlat")

if submit_button:
    if chem1 == chem2:
        st.error("Lütfen iki farklı bileşen seçin.")
    elif not (xB < zF < xD):
        st.error("Kompozisyonlar xB < zF < xD koşulunu sağlamalıdır.")
    else:
        try:
            from src.calculators.separation_calculator import calculate_mccabe_thiele_lines
            
            with st.spinner("Denge verileri ve işletme doğruları hesaplanıyor..."):
                vle_df, q_line_df, rect_line_df, strip_line_df = calculate_mccabe_thiele_lines(
                    chem1, chem2, P, zF, xD, xB, q, R
                )

                st.subheader("McCabe-Thiele Diyagramı")

                # 45 derece doğrusu
                diag_line = alt.Chart(pd.DataFrame({'x': [0, 1], 'y': [0, 1]})).mark_line(color='black', strokeDash=[3,3]).encode(
                    x='x',
                    y='y'
                )

                # Denge eğrisi
                eq_chart = alt.Chart(vle_df).mark_line(color='blue').encode(
                    x=alt.X('x', title=f"{chem1} Mol Fraksiyonu (Sıvı, x)"),
                    y=alt.Y('y', title=f"{chem1} Mol Fraksiyonu (Buhar, y)")
                ).properties(
                    title=f"{chem1}-{chem2} Sistemi @ {P/1e5:.2f} bar"
                )

                # q-doğrusu
                q_chart = alt.Chart(q_line_df).mark_line(color='red').encode(x='x', y='y')
                
                # Zenginleştirme doğrusu
                rect_chart = alt.Chart(rect_line_df).mark_line(color='green').encode(x='x', y='y')

                # Sıyırma doğrusu
                strip_chart = alt.Chart(strip_line_df).mark_line(color='purple').encode(x='x', y='y')

                # Tüm grafikleri birleştir
                final_chart = (diag_line + eq_chart + q_chart + rect_chart + strip_chart).interactive()
                
                st.altair_chart(final_chart, use_container_width=True)
                st.info("Faz 2'de bu grafiğe teorik raf basamakları eklenecektir.")

        except Exception as e:
            st.error(f"Analiz sırasında bir hata oluştu: {e}")
