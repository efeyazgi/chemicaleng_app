import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from src.calculators.separation_calculator import (
    calculate_mccabe_thiele_lines,
    calculate_theoretical_trays,
)

st.set_page_config(page_title="Ayırma İşlemleri", page_icon="⚗️")
st.title("⚗️ Ayırma İşlemleri (McCabe–Thiele Metodu)")
st.markdown("Bu modül, ikili karışımlar için McCabe–Thiele metodunu kullanarak distilasyon kolonlarını analiz eder.")

st.divider()

# --- GİRİŞ ---
with st.expander("🧪 Sistem ve Akış Bilgileri", expanded=True):
    common_chems = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]
    col1, col2 = st.columns(2)
    with col1:
        chem1 = st.selectbox("Hafif Bileşen", common_chems, index=3)
    with col2:
        chem2 = st.selectbox("Ağır Bileşen", common_chems, index=4)

    P = st.number_input("Kolon Basıncı (Pa)", value=101325.0)

    st.markdown("#### 📊 Kompozisyon ve İşletme Koşulları")
    c1, c2, c3 = st.columns(3)
    with c1:
        zF = st.number_input("Besleme Mol Fraksiyonu zF", 0.01, 0.99, 0.50, step=0.01, format="%.2f")
    with c2:
        xD = st.number_input("Distilat Mol Fraksiyonu xD", 0.01, 0.99, 0.95, step=0.01, format="%.2f")
    with c3:
        xB = st.number_input("Dip Mol Fraksiyonu xB", 0.01, 0.99, 0.05, step=0.01, format="%.2f")

    c4, c5 = st.columns(2)
    with c4:
        q = st.number_input("Besleme Kalitesi q", 0.0, 1.0, 1.0, step=0.01, format="%.2f")
    with c5:
        R = st.number_input("Reflüks Oranı R", 0.0, 20.0, 2.5, step=0.1, format="%.2f")

    st.markdown("#### 🔧 Sistem Donanımları")
    colk1, colk2 = st.columns(2)
    with colk1:
        use_reboiler = st.checkbox("Kazan (Reboiler) Var", value=True)
    with colk2:
        use_condenser = st.checkbox("Yoğuşturucu (Condenser) Var", value=True)

    submit = st.button("🧮 Analizi Başlat")

# --- HESAPLAMA ---
if submit:
    if chem1 == chem2:
        st.error("Lütfen iki farklı bileşen seçin.")
    elif not (xB < zF < xD):
        st.error("Kompozisyonlar şu şartı sağlamalı: xB < zF < xD")
    else:
        try:
            with st.spinner("Hesaplanıyor..."):
                vle_df, q_df, rect_df, strip_df = calculate_mccabe_thiele_lines(
                    chem1, chem2, P, zF, xD, xB, q, R
                )
                trays, pts = calculate_theoretical_trays(
                    chem1, chem2, P, zF, xD, xB, q, R
                )

                # 🔐 Tüm değerleri sakla
                st.session_state["mccabe_fig_data"] = {
                    "vle_df": vle_df,
                    "q_df": q_df,
                    "rect_df": rect_df,
                    "strip_df": strip_df,
                    "pts": pts,
                    "chem1": chem1,
                    "chem2": chem2,
                    "P": P,
                    "trays": trays,
                    "zF": zF,
                    "use_reboiler": use_reboiler,
                    "use_condenser": use_condenser
                }

        except Exception as e:
            st.error(f"Analiz sırasında hata: {e}")

# --- SONUÇLAR VE GRAFİK ---
data = st.session_state.get("mccabe_fig_data")
if data:
    st.divider()
    st.subheader("📌 Teorik Sonuçlar")

    # Besleme tepsisi (en yakın adımda)
    feed_index = None
    for i in range(0, len(data["pts"]) - 1, 2):
        x1, _ = data["pts"][i]
        x2, _ = data["pts"][i + 1]
        if x1 <= data["zF"] <= x2 or x2 <= data["zF"] <= x1:
            feed_index = i // 2
            break

    extra = int(data["use_reboiler"]) + int(data["use_condenser"])
    total_trays = data["trays"] + extra

    col1, col2, col3 = st.columns(3)
    col1.metric("🔢 Teorik Raf Sayısı", f"{data['trays']}")
    col2.metric("📍 Besleme Rafı", f"{feed_index + 1 if feed_index is not None else '-'}")
    col3.metric("🧮 Toplam Raf Sayısı", f"{total_trays}")

    # Grafik çizimi
    eq_x = data['vle_df'].x.tolist()
    eq_y = data['vle_df'].y.tolist()
    diag_x, diag_y = [0, 1], [0, 1]
    q_x, q_y = data['q_df'].x.tolist(), data['q_df'].y.tolist()
    r_x, r_y = data['rect_df'].x.tolist(), data['rect_df'].y.tolist()
    s_x, s_y = data['strip_df'].x.tolist(), data['strip_df'].y.tolist()
    step_x, step_y = zip(*data['pts'])

    fig = go.Figure(layout_template='plotly_dark')
    fig.update_layout(
        plot_bgcolor='rgba(30,30,30,1)',
        paper_bgcolor='rgba(30,30,30,1)',
        font=dict(color='white'),
        title=f"McCabe–Thiele Diyagramı: {data['chem1']}–{data['chem2']} @ {data['P']/1e5:.2f} bar",
        xaxis=dict(title=f"{data['chem1']} Mol Fraksiyonu (x)", gridcolor='#444444'),
        yaxis=dict(title=f"{data['chem1']} Mol Fraksiyonu (y)", gridcolor='#444444'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font_color='white')
    )

    fig.add_trace(go.Scatter(x=eq_x, y=eq_y, name="Denge Eğrisi", mode="lines", line=dict(color="cyan")))
    fig.add_trace(go.Scatter(x=diag_x, y=diag_y, name="y = x", mode="lines", line=dict(dash="dot", color="gray")))
    fig.add_trace(go.Scatter(x=q_x, y=q_y, name="q-Line", mode="lines", line=dict(dash="dot", color="orange")))
    fig.add_trace(go.Scatter(x=r_x, y=r_y, name="Zenginleştirme", mode="lines", line=dict(color="lime")))
    fig.add_trace(go.Scatter(x=s_x, y=s_y, name="Sıyrılma", mode="lines", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=step_x, y=step_y, name=f"Raflar ({data['trays']})", mode="lines+markers", line=dict(color="white", dash="dash")))

    fig.add_vline(
        x=data['zF'],
        line=dict(color="yellow", dash='dash'),
        annotation_text=f"zF={data['zF']:.2f}",
        annotation_position="top right",
        annotation_font_color="yellow"
    )

    st.plotly_chart(fig, use_container_width=True)
