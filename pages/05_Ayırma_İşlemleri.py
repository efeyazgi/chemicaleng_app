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

# --- GİRİŞ BÖLÜMÜ ---
with st.expander("🧪 Sistem ve Akış Bilgileri", expanded=True):
    common_chems = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]
    col1, col2 = st.columns(2)
    with col1:
        chem1 = st.selectbox("Hafif Bileşen", common_chems, index=3) # Varsayılan: benzene
    with col2:
        chem2 = st.selectbox("Ağır Bileşen", common_chems, index=4) # Varsayılan: toluene

    P = st.number_input("Kolon Basıncı (Pa)", value=101325.0, format="%.2f")

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
        q = st.number_input("Besleme Kalitesi q", 0.0, 2.0, 1.0, step=0.01, format="%.2f")
    with c5:
        R = st.number_input("Reflüks Oranı R", 0.1, 20.0, 2.5, step=0.1, format="%.1f")

    st.markdown("#### 🔧 Sistem Donanımları")
    colk1, colk2 = st.columns(2)
    with colk1:
        use_reboiler = st.checkbox("Kazan (Reboiler) Var", value=True)
    with colk2:
        # Yoğuşturucu genellikle bir ayırma basamağı sayılmaz, bu yüzden bu seçenek kaldırılabilir
        # veya sadece görsel amaçlı tutulabilir. Şimdilik hesaplamayı etkilemiyor.
        use_condenser = st.checkbox("Yoğuşturucu (Condenser) Var", value=True)

    submit = st.button("🧮 Analizi Başlat")

# --- HESAPLAMA VE OTURUM YÖNETİMİ ---
if submit:
    if chem1 == chem2:
        st.error("Lütfen iki farklı bileşen seçin.")
    elif not (xB < zF < xD):
        st.error("Kompozisyonlar şu şartı sağlamalı: xB < zF < xD")
    else:
        try:
            with st.spinner("Hesaplanıyor..."):
                trays, pts = calculate_theoretical_trays(
                    chem1, chem2, P, zF, xD, xB, q, R
                )
                vle_df, q_df, rect_df, strip_df = calculate_mccabe_thiele_lines(
                    chem1, chem2, P, zF, xD, xB, q, R
                )

                # Sonuçları oturum durumunda sakla
                st.session_state["mccabe_results"] = {
                    "vle_df": vle_df, "q_df": q_df, "rect_df": rect_df,
                    "strip_df": strip_df, "pts": pts, "chem1": chem1,
                    "chem2": chem2, "P": P, "trays": trays, "zF": zF,
                    "use_reboiler": use_reboiler, "use_condenser": use_condenser
                }
                st.rerun() # Sayfayı yeniden çalıştırarak sonuçların gösterilmesini sağla
        except Exception as e:
            st.error(f"Analiz sırasında bir hata oluştu: {e}")

# --- SONUÇLARI GÖSTERME ---
if "mccabe_results" in st.session_state:
    data = st.session_state["mccabe_results"]
    st.divider()
    st.subheader("📌 Teorik Sonuçlar")

    # Besleme rafını bul (daha sağlam bir yöntem)
    feed_tray = None
    # Adımlar (pts) yukarıdan aşağıya (xD'den xB'ye) doğru indiği için x değerleri azalır.
    # Bu yüzden zF'nin hangi iki adımın x değeri arasında kaldığını kontrol ederiz.
    for i in range(0, len(data["pts"]) - 2, 2):
        x_üst, _ = data["pts"][i]      # Rafın üstündeki x
        x_alt, _ = data["pts"][i+2]    # Rafın altındaki x
        if x_alt <= data["zF"] <= x_üst:
            feed_tray = (i // 2) + 1 # Raf numarası 1'den başlar
            break

    # Toplam raf sayısı genellikle teorik raf sayısına eşittir (kazan zaten dahil)
    # veya gerçek plaka sayısı olarak (teorik - 1) gösterilebilir.
    # Kullanıcıya ne gösterileceği tercihe bağlıdır.
    # Burada, kazan bir teorik basamak olduğu için, plaka sayısı trays-1'dir.
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🔢 Teorik Raf Sayısı (Kazan Dahil)", f"{data['trays']}")
    col2.metric("📍 Optimum Besleme Rafı", f"{feed_tray if feed_tray is not None else 'N/A'}")
    col3.metric(" प्लेट Sayısı", f"{data['trays'] - 1 if data['trays'] > 0 else 0}")

    # Grafik çizimi
    fig = go.Figure(layout_template='plotly_dark')
    fig.update_layout(
        plot_bgcolor='rgba(30,30,30,1)', paper_bgcolor='rgba(30,30,30,1)',
        font=dict(color='white'),
        title=f"McCabe–Thiele Diyagramı: {data['chem1']}–{data['chem2']} @ {data['P']/1e5:.2f} bar",
        xaxis=dict(title=f"{data['chem1']} Mol Fraksiyonu (x)", gridcolor='#444444', range=[0,1]),
        yaxis=dict(title=f"{data['chem1']} Mol Fraksiyonu (y)", gridcolor='#444444', range=[0,1]),
        legend=dict(bgcolor='rgba(0,0,0,0)', font_color='white')
    )

    fig.add_trace(go.Scatter(x=data['vle_df'].x, y=data['vle_df'].y, name="Denge Eğrisi", mode="lines", line=dict(color="cyan")))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="y = x", mode="lines", line=dict(dash="dot", color="gray")))
    fig.add_trace(go.Scatter(x=data['q_df'].x, y=data['q_df'].y, name="q-Doğrusu", mode="lines", line=dict(dash="dot", color="orange")))
    fig.add_trace(go.Scatter(x=data['rect_df'].x, y=data['rect_df'].y, name="Zenginleştirme", mode="lines", line=dict(color="lime")))
    fig.add_trace(go.Scatter(x=data['strip_df'].x, y=data['strip_df'].y, name="Soylaştırma", mode="lines", line=dict(color="red")))
    
    step_x, step_y = zip(*data['pts'])
    fig.add_trace(go.Scatter(x=step_x, y=step_y, name=f"Raflar ({data['trays']})", mode="lines+markers", line=dict(color="white", dash="dash")))

    st.plotly_chart(fig, use_container_width=True)
