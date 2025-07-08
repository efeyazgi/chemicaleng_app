import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from src.calculators.heat_transfer_calculator import (
    calculate_planar_wall_heat_transfer,
    compute_planar_temperature_profile,
    calculate_cylindrical_shell_heat_transfer,
    calculate_spherical_shell_heat_transfer,
    MATERIAL_LIBRARY,
    ureg
)

# Türkçe malzeme listesi (parantez içi İngilizce)
material_display = {
    'Bakır (Copper)': 'Copper',
    'Çelik (Steel)': 'Steel',
    'Beton (Concrete)': 'Concrete',
    'Cam (Glass)': 'Glass',
    'Özel (Custom)': 'Custom'
}

# Katmanları başlatan fonksiyon
if 'layers' not in st.session_state:
    st.session_state.layers = [
        {'thickness': 0.1,
         'conductivity': MATERIAL_LIBRARY['Concrete'],
         'material_key': 'Concrete'}
    ]

st.set_page_config(page_title="Isı Transferi Hesaplayıcısı", page_icon="🔥")
st.title("🔥 Isı Transferi Hesaplayıcısı")

# --- Genel Parametreler ---
st.subheader("Genel Parametreler")
t_inner = st.number_input("İç Sıcaklık (K)", value=400.0)
h_inner = st.number_input("İç Konveksiyon Katsayısı (W/m²·K)", value=10.0)
t_outer = st.number_input("Dış Sıcaklık (K)", value=300.0)
h_outer = st.number_input("Dış Konveksiyon Katsayısı (W/m²·K)", value=40.0)
boundary = st.selectbox("Sınır Koşulu Tipi", ["Sıcaklık (T)", "Isı Akısı (q)"])
if boundary == "Isı Akısı (q)":
    q_input = st.number_input("Verilen Q (W)", value=1000.0)

# --- Geometri Seçimi ---
geoms = ["Düzlem Duvar", "Silindirik Kabuk", "Küresel Kabuk"]
geom = st.selectbox("Geometri", geoms)

# --- Düzlem Duvar ---
if geom == "Düzlem Duvar":
    area = st.number_input("Alan (m²)", value=10.0)
    # Katman ekleme/çıkarma
    def add_layer():
        st.session_state.layers.append(
            {'thickness': 0.05,
             'conductivity': MATERIAL_LIBRARY['Concrete'],
             'material_key': 'Concrete'}
        )
    def remove_layer(idx):
        st.session_state.layers.pop(idx)

    st.subheader("Duvar Katmanları")
    for i, layer in enumerate(st.session_state.layers):
        cols = st.columns([3, 2, 2, 1])
        # Malzeme seçimi
        disp_keys = list(material_display.keys())
        current_disp = next((d for d,k in material_display.items() if k==layer.get('material_key')), 'Beton (Concrete)')
        default_idx = disp_keys.index(current_disp)
        selection = cols[0].selectbox(f"Materyal {i+1}", disp_keys, index=default_idx, key=f"mat_sel_{i}")
        mat_key = material_display[selection]
        layer['material_key'] = mat_key
        if mat_key != 'Custom':
            layer['conductivity'] = MATERIAL_LIBRARY[mat_key]
        else:
            layer['conductivity'] = cols[1].number_input(
                f"k{i+1} (W/m·K)", value=layer.get('conductivity', MATERIAL_LIBRARY['Concrete']), key=f"k_{i}")
        layer['thickness'] = cols[2].number_input(
            f"Kalınlık {i+1} (m)", value=layer.get('thickness', 0.05), key=f"t_{i}")
        cols[3].button("❌", key=f"del_{i}", on_click=remove_layer, args=(i,))

    st.button("➕ Katman Ekle", on_click=add_layer)

    if st.button("Hesapla", key="calc_planar"):
        # Hesaplama
        if boundary == "Sıcaklık (T)":
            q, r, err = calculate_planar_wall_heat_transfer(
                t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
            )
            if err:
                st.error(err)
                st.stop()
            st.success(f"Toplam Direnç: {r:.4f} K/W")
            st.success(f"Isı Transfer Hızı Q: {q.magnitude:,.2f} W ({q.to('kilowatt').magnitude:.3f} kW)")
        else:
            _, r, err = calculate_planar_wall_heat_transfer(
                t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
            )
            if err:
                st.error(err)
                st.stop()
            delta_T = q_input * r
            st.success(f"Toplam Direnç: {r:.4f} K/W")
            st.success(f"Sıcaklık Farkı ΔT: {delta_T:,.2f} K")
        # Profil ve direnc dağılımı
        pos, temps, err = compute_planar_temperature_profile(
            t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
        )
        if err:
            st.error(err)
        else:
            df_profile = pd.DataFrame({'Konum (m)': pos, 'Sıcaklık (K)': temps})
            st.line_chart(df_profile.set_index('Konum (m)'))
            labels = ['Konv İç'] + [f"Katman {i+1}" for i in range(len(st.session_state.layers))] + ['Konv Dış']
            r_vals = [1/(h_inner*area)] + [ly['thickness']/(ly['conductivity']*area) for ly in st.session_state.layers] + [1/(h_outer*area)]
            df_r = pd.DataFrame({'Direnç (K/W)': r_vals}, index=labels)
            st.bar_chart(df_r)
            # CSV indir
            csv = df_profile.to_csv(index=False)
            st.download_button('Profil CSV indir', data=csv, file_name='sicaklik_profili.csv', mime='text/csv')

# --- Silindirik ve Küresel Sekmeler ---
else:
    st.info("Silindirik ve küresel kabuk modülleri geliştirme aşamasında.")
