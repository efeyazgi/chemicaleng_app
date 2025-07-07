import streamlit as st
from src.calculators.heat_transfer_calculator import calculate_planar_wall_heat_transfer

st.set_page_config(page_title="Isı Transferi Hesaplayıcısı", page_icon="🔥")

st.title("🔥 Isı Transferi Hesaplayıcısı")

# Session state'i katmanlar için başlatma
if 'layers' not in st.session_state:
    # Başlangıçta bir katman ekle
    st.session_state.layers = [{'thickness': 0.1, 'conductivity': 1.0}]

def add_layer():
    st.session_state.layers.append({'thickness': 0.05, 'conductivity': 0.5})

def remove_layer(index):
    st.session_state.layers.pop(index)

st.subheader("Genel Bilgiler")
area = st.number_input("Duvar Alanı (m²)", value=10.0, min_value=0.01)

col1, col2 = st.columns(2)
with col1:
    t_inner = st.number_input("İç Ortam Sıcaklığı (K)", value=400.0)
    h_inner = st.number_input("İç Konveksiyon Katsayısı (W/m².K)", value=10.0, min_value=0.01)
with col2:
    t_outer = st.number_input("Dış Ortam Sıcaklığı (K)", value=300.0)
    h_outer = st.number_input("Dış Konveksiyon Katsayısı (W/m².K)", value=40.0, min_value=0.01)

st.markdown("---")
st.subheader("Duvar Katmanları")

# Mevcut katmanları göster
for i, layer in enumerate(st.session_state.layers):
    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        st.session_state.layers[i]['thickness'] = st.number_input(
            f"Katman {i+1} Kalınlığı (m)", 
            value=layer['thickness'], 
            format="%.4f", 
            key=f"l_{i}"
        )
    with col2:
        st.session_state.layers[i]['conductivity'] = st.number_input(
            f"Katman {i+1} Isıl İletkenliği (W/m.K)", 
            value=layer['conductivity'], 
            format="%.4f", 
            key=f"k_{i}"
        )
    with col3:
        st.button("🗑️", key=f"del_{i}", on_click=remove_layer, args=(i,), help="Bu katmanı sil")

# Katman ekleme butonu
st.button("➕ Katman Ekle", on_click=add_layer)

st.markdown("---")

if st.button("Isı Transfer Hızını Hesapla"):
    if not st.session_state.layers:
        st.warning("Lütfen en az bir duvar katmanı ekleyin.")
    else:
        q, r_total, error = calculate_planar_wall_heat_transfer(
            t_inner, h_inner, t_outer, h_outer, area, st.session_state.layers
        )
        
        if error:
            st.error(error)
        else:
            st.success(f"Toplam Isıl Direnç: **{r_total:.4f} K/W**")
            st.success(f"Isı Transfer Hızı (Q): **{q:,.2f} W** ({q/1000:,.3f} kW)")
