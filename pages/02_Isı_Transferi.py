import streamlit as st
st.set_page_config(page_title="Isı Transferi Hesaplayıcısı", page_icon="🔥")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
# src.calculators... importlarınızın doğru çalıştığını varsayıyoruz.
# Eğer bu importta hata alırsanız, dosya yolunu kontrol etmeniz gerekebilir.
from src.calculators.heat_transfer_calculator import (
    calculate_planar_wall_heat_transfer,
    compute_planar_temperature_profile,
    calculate_cylindrical_shell_heat_transfer,
    calculate_spherical_shell_heat_transfer,
    MATERIAL_LIBRARY,
    ureg
)

# --- GİRİŞ KONTROLÜ (GÜNCELLENMİŞ BLOK) ---
# Bu blok, sayfaya erişim için kullanıcının oturum açıp açmadığını ve misafir olup olmadığını kontrol eder.
# Bu yöntem, silinen auth.py dosyası yerine doğrudan st.session_state'i kullanır.
if not st.session_state.get("logged_in", False):
    st.error("Bu sayfayı görüntülemek için lütfen ana sayfadan giriş yapın.")
    # Kullanıcıyı ana sayfaya yönlendirmek için bir link ekleniyor.
    # Ana sayfa dosyanızın adının "00_Ana_Sayfa.py" olduğunu varsayıyoruz.
    st.page_link("00_Ana_Sayfa.py", label="Ana Sayfaya Dön", icon="🏠")
    st.stop() # Sayfanın geri kalanının yüklenmesini engeller.

# Misafir kullanıcıların bu modüle erişimini engelleme
if st.session_state.get("is_guest", False):
    st.warning("Bu modül yalnızca kayıtlı kullanıcılar içindir.")
    st.info("Lütfen ana sayfaya dönüp kayıtlı bir kullanıcı ile giriş yapın.")
    st.page_link("00_Ana_Sayfa.py", label="Ana Sayfaya Dön", icon="🏠")
    st.stop()

# --- SAYFA YAPILANDIRMASI VE BAŞLIK ---
st.title("🔥 Isı Transferi Hesaplayıcısı")
st.markdown("Bu modül, çok katmanlı duvarlarda iletim ve konveksiyon etkilerini göz önünde bulundurarak ısı transferi hesaplamaları yapmanızı sağlar.")

# Başlangıç katmanı
if 'layers' not in st.session_state:
    st.session_state.layers = [{
        'thickness': 0.1,
        'conductivity': MATERIAL_LIBRARY['Concrete'],
        'material_key': 'Concrete'
    }]

material_display = {
    'Bakır (Copper)': 'Copper',
    'Çelik (Steel)': 'Steel',
    'Beton (Concrete)': 'Concrete',
    'Cam (Glass)': 'Glass',
    'Özel (Custom)': 'Custom'
}

st.divider()

# GENEL PARAMETRELER
with st.expander("⚙️ Genel Parametreler", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        t_inner = st.number_input("İç Sıcaklık (K)", value=400.0)
        h_inner = st.number_input("İç Konveksiyon Katsayısı (W/m²·K)", value=10.0)
        boundary = st.selectbox("Sınır Koşulu Tipi", ["Sıcaklık (T)", "Isı Akısı (q)"])
        if boundary == "Isı Akısı (q)":
            q_input = st.number_input("Verilen Q (W)", value=1000.0)
    with col2:
        t_outer = st.number_input("Dış Sıcaklık (K)", value=300.0)
        h_outer = st.number_input("Dış Konveksiyon Katsayısı (W/m²·K)", value=40.0)
        geom = st.selectbox("Geometri", ["Düzlem Duvar", "Silindirik Kabuk", "Küresel Kabuk"])

st.divider()

# KATMANLAR
if geom == "Düzlem Duvar":
    with st.expander("🧱 Duvar Katmanları", expanded=True):
        area = st.number_input("Alan (m²)", value=10.0)

        def add_layer():
            st.session_state.layers.append({
                'thickness': 0.05,
                'conductivity': MATERIAL_LIBRARY['Concrete'],
                'material_key': 'Concrete'
            })
        def remove_layer(idx):
            st.session_state.layers.pop(idx)

        for i, layer in enumerate(st.session_state.layers):
            cols = st.columns([3, 2, 2, 1])
            disp_keys = list(material_display.keys())
            current_disp = next((d for d, k in material_display.items() if k == layer.get('material_key')), 'Beton (Concrete)')
            default_idx = disp_keys.index(current_disp)
            selection = cols[0].selectbox(f"Materyal {i+1}", disp_keys, index=default_idx, key=f"mat_sel_{i}")
            mat_key = material_display[selection]
            layer['material_key'] = mat_key
            if mat_key != 'Custom':
                layer['conductivity'] = MATERIAL_LIBRARY[mat_key]
            else:
                layer['conductivity'] = cols[1].number_input(
                    f"k{i+1} (W/m·K)", value=layer.get('conductivity', 1.0), key=f"k_{i}")
            layer['thickness'] = cols[2].number_input(
                f"Kalınlık {i+1} (m)", value=layer.get('thickness', 0.05), key=f"t_{i}")
            cols[3].button("❌", key=f"del_{i}", on_click=remove_layer, args=(i,))
        
        st.button("➕ Katman Ekle", on_click=add_layer)

    # Hesapla Butonu
    if st.button("🧮 Hesapla", key="calc_planar"):
        if boundary == "Sıcaklık (T)":
            q, r, err = calculate_planar_wall_heat_transfer(
                t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
            )
            if err:
                st.error(err)
                st.stop()
            st.success(f"Toplam Isıl Direnç: {r:.4f} K/W")
            st.success(f"Isı Transfer Hızı Q: {q.magnitude:,.2f} W ({q.to('kilowatt').magnitude:.3f} kW)")
        else:
            _, r, err = calculate_planar_wall_heat_transfer(
                t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
            )
            if err:
                st.error(err)
                st.stop()
            delta_T = q_input * r
            st.success(f"Toplam Isıl Direnç: {r:.4f} K/W")
            st.success(f"Sıcaklık Farkı ΔT: {delta_T:,.2f} K")

        # Profil ve direnç dağılımı
        pos, temps, err = compute_planar_temperature_profile(
            t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
        )
        if err:
            st.error(err)
        else:
            # 📈 Sıcaklık Profili Grafiği (Matplotlib)
            st.subheader("🌡️ Sıcaklık Profili (Konum vs Sıcaklık)")
            fig1, ax1 = plt.subplots()
            ax1.plot(pos, temps, marker="o", color="cyan")
            ax1.set_xlabel("Duvar İçindeki Konum (m)")
            ax1.set_ylabel("Sıcaklık (K)")
            ax1.set_title("Katmanlar Boyunca Sıcaklık Değişimi")
            ax1.grid(True)
            st.pyplot(fig1)

            # 📊 Isıl Direnç Dağılımı (Yatay Bar)
            st.subheader("📊 Isıl Direnç Dağılımı")
            labels = ['Konv. İç'] + [f"Katman {i+1}" for i in range(len(st.session_state.layers))] + ['Konv. Dış']
            r_vals = [1/(h_inner*area)] + [ly['thickness']/(ly['conductivity']*area) for ly in st.session_state.layers] + [1/(h_outer*area)]

            fig2, ax2 = plt.subplots()
            ax2.barh(labels, r_vals, color="skyblue")
            ax2.set_xlabel("Direnç (K/W)")
            ax2.set_title("Her Katmanın ve Konveksiyonun Toplam Dirence Katkısı")
            st.pyplot(fig2)

            # 📥 CSV İndir
            df_profile = pd.DataFrame({'Konum (m)': pos, 'Sıcaklık (K)': temps})
            st.download_button('📥 Sıcaklık Profili (CSV)', data=df_profile.to_csv(index=False),
                                file_name='sicaklik_profili.csv', mime='text/csv')

else:
    st.info("Silindirik ve küresel kabuk modülleri şu an için geliştirme aşamasındadır.")
