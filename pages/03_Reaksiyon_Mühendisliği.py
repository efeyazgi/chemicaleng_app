import streamlit as st
import numpy as np

# Grafik kütüphanesi: Önce matplotlib, olmazsa plotly
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None
    import plotly.graph_objs as go

from src.calculators.reaction_calculator import (
    calculate_rate_constant,
    calculate_reactor_volume,
    calculate_batch_time,
)

st.set_page_config(page_title="Reaktör Tasarımı", page_icon="⚛️")
st.title("⚛️ Reaktör Tasarımı")
st.markdown("Bu modül, CSTR, PFR ve kesikli reaktörler için dönüşüm, hacim ve süre hesaplamaları yapmanıza olanak tanır.")

st.divider()

# --- 1. Kinetik Parametreler ---
with st.expander("⚙️ Kinetik Parametreler", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        f_a0 = st.number_input("Fₐ₀ (mol/s)", value=1.0)
        c_a0 = st.number_input("Cₐ₀ (mol/m³)", value=100.0)
    with col2:
        model = st.selectbox("Kinetik Model", ["Cₐⁿ", "Cₐⁿ·Cᵦᵐ"], index=0)
        if model == "Cₐⁿ·Cᵦᵐ":
            c_b0 = st.number_input("Cᵦ₀ (mol/m³)", value=100.0)
            m = st.number_input("Mertebe m", value=1.0)
        else:
            c_b0 = None
            m = 0.0

# --- 2. Sabit k veya Arrhenius ---
with st.expander("📐 Sabit k veya Arrhenius Parametreleri", expanded=True):
    use_arrh = st.checkbox("Arrhenius kullan", value=False)
    if use_arrh:
        # Toplam mertebe k birimini etkiler
        overall_order = st.number_input("Toplam Mertebe (n + m)", value=1.0, min_value=0.0)
        k0 = st.number_input("k₀ (birimi mertebeye bağlı)", value=1e3, format="%.3e")
        Ea = st.number_input("Aktivasyon Enerjisi Ea (J/mol)", value=50000.0)
        T = st.number_input("Sıcaklık T (K)", value=298.15)
        k = calculate_rate_constant(k0, Ea, T, overall_order=overall_order)
        try:
            st.success(f"Hesaplanan k = {k.magnitude:.3e} {k.to_base_units().units:~P}")
        except Exception:
            st.success(f"Hesaplanan k = {k}")
    else:
        k = st.number_input("k (sayısal)", value=0.1)

# --- 3. Reaktör Türü & Hesaplama ---
with st.expander("🧪 Reaktör Tipi ve Hesaplama", expanded=True):
    X = st.slider("Dönüşüm X", 0.01, 0.99, 0.50, step=0.01)
    n = st.number_input("Mertebe n", value=1.0)
    reactor_type = st.selectbox("Reaktör Tipi", ["CSTR (DKTR)", "PFR (PAR)", "Batch (Kesikli)"])

    st.markdown("#### Stokiyometri ve Faz")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        a = st.number_input("a (A katsayısı)", value=1.0, min_value=0.0)
    with sc2:
        b = st.number_input("b (B katsayısı)", value=1.0, min_value=0.0)
    with sc3:
        phase_label = st.selectbox("Faz", ["Sıvı", "Gaz"], index=0)
        phase = "liquid" if phase_label == "Sıvı" else "gas"

    eps = 0.0
    if phase == "gas":
        eps = st.number_input("ε (Hacim değişimi parametresi)", value=0.0, format="%.3f")

    if st.button("🧮 Hesapla", use_container_width=True):
        st.subheader("📌 Hesap Sonuçları")

        if reactor_type.startswith("CSTR"):
            vol = calculate_reactor_volume(
                f_a0, c_a0, k, X, n, 'CSTR', C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
            )
            L = vol.to('liter')
            st.success(f"Gerekli Hacim: {vol.magnitude:.3f} m³  ({L.magnitude:.2f} L)")

            xs = np.linspace(0.01, X, 50)
            vs = [
                calculate_reactor_volume(
                    f_a0, c_a0, k, xi, n, 'CSTR', C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
                ).magnitude for xi in xs
            ]
            if plt is not None:
                fig, ax = plt.subplots()
                ax.plot(xs, vs, color='orange')
                ax.set_xlabel("Dönüşüm X")
                ax.set_ylabel("Reaktör Hacmi V (m³)")
                ax.set_title("CSTR için X - V Eğrisi")
                ax.grid(True)
                st.pyplot(fig)
            else:
                fig = go.Figure()
                fig.add_scatter(x=xs, y=vs, mode='lines', line=dict(color='orange'), name='V')
                fig.update_layout(xaxis_title='Dönüşüm X', yaxis_title='Reaktör Hacmi V (m³)', title='CSTR için X - V Eğrisi')
                st.plotly_chart(fig, use_container_width=True)

        elif reactor_type.startswith("PFR"):
            vol = calculate_reactor_volume(
                f_a0, c_a0, k, X, n, 'PFR', C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
            )
            L = vol.to('liter')
            st.success(f"Gerekli Hacim: {vol.magnitude:.3f} m³  ({L.magnitude:.2f} L)")

            xs = np.linspace(0.01, X, 50)
            vs = [
                calculate_reactor_volume(
                    f_a0, c_a0, k, xi, n, 'PFR', C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
                ).magnitude for xi in xs
            ]
            if plt is not None:
                fig, ax = plt.subplots()
                ax.plot(xs, vs, color='green')
                ax.set_xlabel("Dönüşüm X")
                ax.set_ylabel("Reaktör Hacmi V (m³)")
                ax.set_title("PFR için X - V Eğrisi")
                ax.grid(True)
                st.pyplot(fig)
            else:
                fig = go.Figure()
                fig.add_scatter(x=xs, y=vs, mode='lines', line=dict(color='green'), name='V')
                fig.update_layout(xaxis_title='Dönüşüm X', yaxis_title='Reaktör Hacmi V (m³)', title='PFR için X - V Eğrisi')
                st.plotly_chart(fig, use_container_width=True)

        else:
            time = calculate_batch_time(
                c_a0, k, X, n, C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
            )
            t_h = time.to('hour')
            st.success(f"Gerekli Süre: {time.magnitude:.2f} saniye ({t_h.magnitude:.2f} saat)")

            xs = np.linspace(0.01, X, 50)
            ts = [
                calculate_batch_time(
                    c_a0, k, xi, n, C_B0=c_b0, m=m, a=a, b=b, phase=phase, epsilon=eps
                ).magnitude for xi in xs
            ]
            if plt is not None:
                fig, ax = plt.subplots()
                ax.plot(ts, xs, color='purple')
                ax.set_xlabel("Zaman t (s)")
                ax.set_ylabel("Dönüşüm X")
                ax.set_title("Batch için X - t Eğrisi")
                ax.grid(True)
                st.pyplot(fig)
            else:
                fig = go.Figure()
                fig.add_scatter(x=ts, y=xs, mode='lines', line=dict(color='purple'), name='X')
                fig.update_layout(xaxis_title='Zaman t (s)', yaxis_title='Dönüşüm X', title='Batch için X - t Eğrisi')
                st.plotly_chart(fig, use_container_width=True)
