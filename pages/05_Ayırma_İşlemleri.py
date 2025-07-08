import streamlit as st
import pandas as pd
import plotly.graph_objs as go

from src.calculators.separation_calculator import (
    calculate_mccabe_thiele_lines,
    calculate_theoretical_trays,
)

st.set_page_config(page_title="Ayırma İşlemleri", page_icon="⚗️")
st.title("⚗️ Ayırma İşlemleri")

st.info("Bu modül, ikili karışımlar için McCabe-Thiele metodunu kullanarak distilasyon kolonlarını analiz eder.")
st.warning("**Not:** Bu özellik deneyseldir. Bazı sistemler veya koşullar için sayısal olarak kararlı sonuçlar üretemeyebilir.")

with st.form("mccabe_form"):
    st.subheader("Sistem ve Besleme Bilgileri")
    common_chems = [
        "water","ethanol","methanol","benzene","toluene",
        "acetone","ammonia","carbon dioxide","oxygen",
        "nitrogen","air","methane","propane","butane"
    ]
    col1, col2 = st.columns(2)
    with col1:
        chem1 = st.selectbox("Hafif Bileşen", common_chems, index=3)
    with col2:
        chem2 = st.selectbox("Ağır Bileşen", common_chems, index=4)

    P = st.number_input("Kolon Basıncı (Pa)", value=101325.0)

    st.subheader("Kompozisyon ve Akış Koşulları")
    c1, c2, c3 = st.columns(3)
    with c1:
        zF = st.number_input("Besleme Komp. (zF)", 0.01, 0.99, 0.50, format="%.2f")
    with c2:
        xD = st.number_input("Distilat Komp. (xD)", 0.01, 0.99, 0.95, format="%.2f")
    with c3:
        xB = st.number_input("Dip Ürün Komp. (xB)", 0.01, 0.99, 0.05, format="%.2f")

    c1, c2 = st.columns(2)
    with c1:
        q = st.number_input("Besleme Kalitesi (q)", 0.0, 1.0, 1.0, format="%.2f")
    with c2:
        R = st.number_input("Reflüks Oranı (R)", 0.0, 20.0, 2.5, format="%.2f")

    submit = st.form_submit_button("Analizi Başlat")

if submit:
    if chem1 == chem2:
        st.error("Lütfen iki farklı bileşen seçin.")
    elif not (xB < zF < xD):
        st.error("Kompozisyonlar xB < zF < xD koşulunu sağlamalıdır.")
    else:
        try:
            with st.spinner("Hesaplanıyor..."):
                vle_df, q_df, rect_df, strip_df = calculate_mccabe_thiele_lines(
                    chem1, chem2, P, zF, xD, xB, q, R
                )
                trays, pts = calculate_theoretical_trays(
                    chem1, chem2, P, zF, xD, xB, q, R
                )

            # Veri dizileri
            eq_x, eq_y       = vle_df.x.tolist(), vle_df.y.tolist()
            diag_x, diag_y   = [0,1], [0,1]
            q_x, q_y         = q_df.x.tolist(), q_df.y.tolist()
            r_x, r_y         = rect_df.x.tolist(), rect_df.y.tolist()
            s_x, s_y         = strip_df.x.tolist(), strip_df.y.tolist()
            step_x, step_y   = zip(*pts)

            # Renk ve stil
            colors = {
                'equil':'#1f77b4','diag':'#888888','qline':'#ffa000',
                'rectify':'#2ca02c','strip':'#d62728','steps':'#eeeeee','feed':'#ff7f0e'
            }

            # Figür
            fig = go.Figure(layout_template='plotly_dark')
            fig.update_layout(
                plot_bgcolor='rgba(30,30,30,1)',
                paper_bgcolor='rgba(30,30,30,1)',
                font=dict(color='white'),
                title=f"McCabe–Thiele: {chem1}-{chem2} Sistemi @ {P/1e5:.2f} bar",
                xaxis=dict(
                    title=f"{chem1} Mol Fraksiyonu (Sıvı, x)",
                    gridcolor='#444444', zerolinecolor='#888888',
                    showline=True, linecolor='#666666', mirror=True
                ),
                yaxis=dict(
                    title=f"{chem1} Mol Fraksiyonu (Buhar, y)",
                    gridcolor='#444444', zerolinecolor='#888888',
                    showline=True, linecolor='#666666', mirror=True
                ),
                legend=dict(font_color='white', bgcolor='rgba(0,0,0,0)')
            )

            # Feed hattı
            fig.add_vline(
                x=zF,
                line=dict(color=colors['feed'], dash='dash', width=2),
                annotation_text=f"zF={zF:.2f}",
                annotation_position="top right",
                annotation_font_color=colors['feed']
            )

            # Trace’ler
            fig.add_trace(go.Scatter(x=eq_x, y=eq_y, mode='lines',
                                     name='Equilibrium', line=dict(color=colors['equil'], width=2)))
            fig.add_trace(go.Scatter(x=diag_x, y=diag_y, mode='lines',
                                     name='y=x', line=dict(color=colors['diag'], dash='dash')))
            fig.add_trace(go.Scatter(x=q_x, y=q_y, mode='lines',
                                     name='q-line', line=dict(color=colors['qline'], dash='dot')))
            fig.add_trace(go.Scatter(x=r_x, y=r_y, mode='lines',
                                     name='Rectifying', line=dict(color=colors['rectify'], width=2)))
            fig.add_trace(go.Scatter(x=s_x, y=s_y, mode='lines',
                                     name='Stripping', line=dict(color=colors['strip'], width=2)))
            fig.add_trace(go.Scatter(x=list(step_x), y=list(step_y),
                                     mode='lines+markers', name=f'Steps ({trays})',
                                     line=dict(color=colors['steps'], dash='dot'),
                                     marker=dict(size=6, color=colors['steps'])))

            # Çizimi göster
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"Teorik Tepsi Sayısı: {trays}")

        except Exception as e:
            st.error(f"Analiz sırasında hata: {e}")
