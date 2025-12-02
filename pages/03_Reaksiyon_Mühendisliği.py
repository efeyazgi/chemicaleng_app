
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from src.calculators.reaction_calculator import (
    calculate_rate_constant,
    calculate_reactor_volume,
    calculate_batch_time,
    generate_levenspiel_data
)
from src.utils.unit_manager import render_global_settings_sidebar, render_local_unit_override, convert_value
from src.utils.ui_helper import load_css, render_header, render_card, render_info_card

load_css()

st.set_page_config(page_title="Reaksiyon Mühendisliği", page_icon="⚛️", layout="wide")

render_header("Reaksiyon Mühendisliği", "⚛️")
st.markdown("İdeal reaktörlerin (CSTR, PFR, Batch) tasarımı ve analizi.")
st.markdown("---")

# --- GİRİŞLER (SOL KOLON) ---
col_left, col_right = st.columns([1, 2])

with col_left:
    # Global Ayarlar
    render_global_settings_sidebar()
    
    # Yerel Ayarlar
    unit_system, units = render_local_unit_override("reaction")
    
    st.subheader("⚙️ Parametreler")
    
    # 1. Reaksiyon Kinetiği
    with st.expander("Kinetik Model", expanded=True):
        rate_model = st.selectbox("Hız İfadesi", ["Üs Yasası (Power Law)", "Çift Moleküllü (Bimolecular)"])
        
        if "Üs Yasası" in rate_model:
            st.latex(r"r_A = k C_A^n")
        else:
            st.latex(r"r_A = k C_A^n C_B^m")
        
        col_n, col_m = st.columns(2)
        with col_n:
            n = st.number_input("Mertebe (n)", value=1.0, min_value=0.0, step=0.1)
        
        m = 0.0
        if "Bimolecular" in rate_model:
            with col_m:
                m = st.number_input("Mertebe (m)", value=1.0, min_value=0.0, step=0.1)
        
        # Hız Sabiti (k)
        k_method = st.radio("Hız Sabiti (k) Girişi:", ["Doğrudan Gir", "Arrhenius ($k = A e^{-E_a/RT}$)"])
        
        if k_method == "Doğrudan Gir":
            k_val = st.number_input("Hız Sabiti (k)", value=0.1, format="%.4f")
            k = k_val # Birim hesaplayıcıda halledilecek
        else:
            A = st.number_input("Frekans Faktörü (A)", value=1e5, format="%.2e")
            
            ea_unit = units.get('ActivationEnergy', 'J/mol')
            Ea_input = st.number_input(f"Aktivasyon Enerjisi ($E_a$, {ea_unit})", value=50000.0)
            # SI'ya çevir (J/mol)
            Ea = convert_value(Ea_input, ea_unit, 'J/mol')
            
            t_unit = units.get('T', 'K')
            T_input = st.number_input(f"Sıcaklık (T, {t_unit})", value=300.0)
            # SI'ya çevir (K)
            T = convert_value(T_input, t_unit, 'K')
            
            # Toplam mertebe
            overall_order = n + m
            try:
                k_pint = calculate_rate_constant(A, Ea, T, overall_order=overall_order)
                k = k_pint.magnitude
                st.info(f"Hesaplanan k: **{k:.4e}**")
            except Exception as e:
                st.error(f"Hata: {e}")
                k = 0.1

    # 2. Reaktör ve İşletme
    with st.expander("Reaktör Koşulları", expanded=True):
        reactor_type = st.selectbox("Reaktör Tipi", ["CSTR (Sürekli Karıştırmalı)", "PFR (Piston Akışlı)", "Batch (Kesikli)"])
        
        phase_label = st.selectbox("Faz", ["Sıvı (Liquid)", "Gaz (Gas)"])
        phase = "liquid" if "Sıvı" in phase_label else "gas"
        
        epsilon = 0.0
        if phase == "gas":
            st.info("Gaz fazı için hacim değişimi ($V = V_0(1 + \\epsilon X)$) dikkate alınır.")
            epsilon = st.number_input("Genleşme Faktörü ($\\epsilon$)", value=0.0, step=0.1, help="$\\epsilon = y_{A0} \\delta$")
        
        st.markdown("#### Giriş Koşulları")
        
        flow_unit = units.get('Flow', 'mol/s')
        F_A0_input = st.number_input(f"Molar Akış ($F_{{A0}}$, {flow_unit})", value=1.0, min_value=0.01)
        # SI'ya çevir (mol/s)
        F_A0 = convert_value(F_A0_input, flow_unit, 'mol/s')
        
        conc_unit = units.get('Conc', 'mol/m**3')
        C_A0_input = st.number_input(f"Giriş Kons. ($C_{{A0}}$, {conc_unit})", value=100.0, min_value=0.1)
        # SI'ya çevir (mol/m3)
        C_A0 = convert_value(C_A0_input, conc_unit, 'mol/m**3')
        
        C_B0 = None
        b_coeff = 0.0
        if "Bimolecular" in rate_model:
            C_B0_input = st.number_input(f"Giriş Kons. ($C_{{B0}}$, {conc_unit})", value=100.0, min_value=0.0)
            C_B0 = convert_value(C_B0_input, conc_unit, 'mol/m**3')
            st.markdown("#### Stokiyometri ($A + (b/a)B \\rightarrow ...$)")
            b_coeff = st.number_input("Katsayı oranı (b/a)", value=1.0, min_value=0.0)
        
        st.markdown("#### Hedef")
        X_target = st.slider("Hedef Dönüşüm ($X$)", 0.01, 0.99, 0.8, step=0.01)
        
    calc_btn = st.button("🚀 Hesapla", type="primary", use_container_width=True)

# --- SONUÇLAR (SAĞ KOLON) ---
with col_right:
    if calc_btn:
        try:
            # Hesaplama
            if reactor_type.startswith("Batch"):
                # Batch için F_A0 yerine V_reactor veya N_A0 gerekir ama fonksiyonumuz C_A0 ve k kullanıyor, süre dönüyor.
                # Batch time calculation
                res_time = calculate_batch_time(
                    C_A0, k, X_target, n, C_B0=C_B0, m=m, b=b_coeff, phase=phase, epsilon=epsilon
                )
                res_time_si = res_time.magnitude # saniye
                
                target_time_unit = units.get('Time', 's')
                res_val = convert_value(res_time_si, 's', target_time_unit)
                res_unit = target_time_unit
                
                st.success(f"⏱️ Gerekli Süre: **{res_val:.2f} {res_unit}**")
                render_card("Gerekli Süre", f"{res_val:.2f}", unit=res_unit)
                
                # Batch için Hacim hesabı kullanıcıdan gelmeli veya F_A0 ile alakasız.
                # Biz sadece süreyi bulduk.
                
            else:
                # CSTR / PFR
                r_type_code = 'CSTR' if 'CSTR' in reactor_type else 'PFR'
                res_vol = calculate_reactor_volume(
                    F_A0, C_A0, k, X_target, n, r_type_code, C_B0=C_B0, m=m, b=b_coeff, phase=phase, epsilon=epsilon
                )
                res_vol_si = res_vol.magnitude # m3
                
                target_vol_unit = units.get('Vol', 'm**3')
                res_val = convert_value(res_vol_si, 'm**3', target_vol_unit)
                res_unit = target_vol_unit
                
                st.success(f"📦 Gerekli Hacim: **{res_val:.4f} {res_unit}**")
                render_card("Gerekli Hacim", f"{res_val:.4f}", unit=res_unit)
                
                # Karşılaştırma (Diğer reaktör tipi ne olurdu?)
                other_type = 'PFR' if r_type_code == 'CSTR' else 'CSTR'
                other_vol = calculate_reactor_volume(
                    F_A0, C_A0, k, X_target, n, other_type, C_B0=C_B0, m=m, b=b_coeff, phase=phase, epsilon=epsilon
                )
                other_vol_val = convert_value(other_vol.magnitude, 'm**3', target_vol_unit)
                st.info(f"ℹ️ Karşılaştırma: Aynı dönüşüm için {other_type} hacmi **{other_vol_val:.4f} {res_unit}** olurdu.")

            # --- GRAFİKLER ---
            st.markdown("### 📈 Analiz Grafikleri")
            
            # Veri Üretimi
            df_lev = generate_levenspiel_data(
                C_A0, k, 0.99, n, C_B0=C_B0, m=m, b=b_coeff, phase=phase, epsilon=epsilon
            )
            
            # 1. Levenspiel Plot (1/-rA vs X)
            # Area shading logic
            
            lev_chart = alt.Chart(df_lev).mark_line(color='#1f77b4', strokeWidth=3).encode(
                x=alt.X('X', title='Dönüşüm (X)'),
                y=alt.Y('inv_rate', title='1 / (-rA) [m³ s / mol]'),
                tooltip=['X', 'rate', 'inv_rate']
            ).properties(title="Levenspiel Diyagramı")
            
            # Alan tarama (Reaktör tipine göre)
            area_data = df_lev[df_lev['X'] <= X_target]
            
            if reactor_type.startswith("CSTR"):
                # CSTR: Dikdörtgen alan (X_target * (1/-rA)|X_target)
                # Altair'de bunu çizmek için özel bir dataframe lazım
                y_at_X = df_lev.iloc[(df_lev['X'] - X_target).abs().argsort()[:1]]['inv_rate'].values[0]
                rect_df = pd.DataFrame([
                    {'x': 0, 'y': 0, 'x2': X_target, 'y2': y_at_X}
                ])
                area_chart = alt.Chart(rect_df).mark_rect(opacity=0.3, color='orange').encode(
                    x='x', y='y', x2='x2', y2='y2'
                )
                final_chart = lev_chart + area_chart
                
            elif reactor_type.startswith("PFR"):
                # PFR: Eğri altındaki alan
                area_chart = alt.Chart(area_data).mark_area(opacity=0.3, color='green').encode(
                    x='X', y='inv_rate'
                )
                final_chart = lev_chart + area_chart
            else:
                final_chart = lev_chart
                
            st.altair_chart(final_chart, use_container_width=True)
            
            # 2. Konsantrasyon Profili (CA vs X veya V)
            # X ekseni Dönüşüm olsun, daha evrensel.
            conc_chart = alt.Chart(df_lev).mark_line(color='#d62728').encode(
                x=alt.X('X', title='Dönüşüm (X)'),
                y=alt.Y('CA', title='Konsantrasyon CA (mol/m³)'),
                tooltip=['X', 'CA']
            ).properties(title="Konsantrasyon Profili")
            
            st.altair_chart(conc_chart, use_container_width=True)
            
        except Exception as e:
            st.error(f"Hesaplama Hatası: {e}")
            # st.exception(e) # Debug
    else:
        st.info("👈 Parametreleri ayarlayıp 'Hesapla' butonuna basın.")
