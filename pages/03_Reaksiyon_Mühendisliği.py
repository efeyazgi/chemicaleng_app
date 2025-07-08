import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from src.calculators.reaction_calculator import (
    calculate_rate_constant,
    calculate_reactor_volume,
    calculate_batch_time
)

st.set_page_config(page_title="Reaktör Tasarımı", page_icon="⚛️")
st.title("⚛️ Reaktör Tasarımı")

# --- Girdi Parametreleri ---
st.subheader("Kinetik Parametreler")
f_a0 = st.number_input("F_A0 (mol/s)", value=1.0)
c_a0 = st.number_input("C_A0 (mol/m³)", value=100.0)
model = st.selectbox("Kinetik Modeli", ["CA^n", "CA^n·CB^m"])
if model == "CA^n·CB^m":
    c_b0 = st.number_input("C_B0 (mol/m³)", value=100.0)
    m = st.number_input("Mertebe m", value=1.0)
else:
    c_b0 = None
    m = 0.0
st.markdown("---")

st.subheader("Arrhenius veya Sabit k")
use_arrh = st.checkbox("Arrhenius kinetiği kullan", value=False)
if use_arrh:
    k0 = st.number_input("k0 (1/s)", value=1e3, format="%.3e")
    Ea = st.number_input("Ea (J/mol)", value=50000.0)
    T = st.number_input("T (K)", value=298.15)
    k = calculate_rate_constant(k0, Ea, T)
    st.write(f"Hesaplanan k: {k:.3e} 1/s")
else:
    k = st.number_input("k (1/s)", value=0.1)

st.markdown("---")

st.subheader("Hacim / Süre Hesaplama")
X = st.slider("Dönüşüm X", 0.01, 0.99, 0.5, step=0.01)
n = st.number_input("Mertebe n", value=1.0)
reactor_type = st.selectbox("Reaktör Tipi", ["CSTR (DKTR)", "PFR (PAR)", "Batch (Kesikli)"])

if st.button("Hesapla"):
    if reactor_type.startswith("CSTR"):
        vol = calculate_reactor_volume(f_a0, c_a0, k, X, n, 'CSTR', C_B0=c_b0, m=m)
        L = vol.to('liter')
        st.success(f"Gerekli Hacim: {vol.magnitude:.3f} m³ ({L.magnitude:.2f} L)")
        xs = np.linspace(0.01, X, 50)
        vs = [calculate_reactor_volume(f_a0, c_a0, k, xi, n, 'CSTR', C_B0=c_b0, m=m).magnitude for xi in xs]
        fig, ax = plt.subplots()
        ax.plot(xs, vs)
        ax.set_xlabel("X")
        ax.set_ylabel("V (m³)")
        ax.set_title("CSTR için X-V Eğrisi")
        st.pyplot(fig)

    elif reactor_type.startswith("PFR"):
        vol = calculate_reactor_volume(f_a0, c_a0, k, X, n, 'PFR', C_B0=c_b0, m=m)
        L = vol.to('liter')
        st.success(f"Gerekli Hacim: {vol.magnitude:.3f} m³ ({L.magnitude:.2f} L)")
        xs = np.linspace(0.01, X, 50)
        vs = [calculate_reactor_volume(f_a0, c_a0, k, xi, n, 'PFR', C_B0=c_b0, m=m).magnitude for xi in xs]
        fig, ax = plt.subplots()
        ax.plot(xs, vs)
        ax.set_xlabel("X")
        ax.set_ylabel("V (m³)")
        ax.set_title("PFR için X-V Eğrisi")
        st.pyplot(fig)

    else:
        time = calculate_batch_time(c_a0, k, X, n, C_B0=c_b0, m=m)
        t_h = time.to('hour')
        st.success(f"Gerekli Süre: {time.magnitude:.2f} s ({t_h.magnitude:.2f} h)")
        xs = np.linspace(0.01, X, 50)
        ts = [calculate_batch_time(c_a0, k, xi, n, C_B0=c_b0, m=m).magnitude for xi in xs]
        fig, ax = plt.subplots()
        ax.plot(ts, xs)
        ax.set_xlabel("t (s)")
        ax.set_ylabel("X")
        ax.set_title("Batch için X-t Eğrisi")
        st.pyplot(fig)