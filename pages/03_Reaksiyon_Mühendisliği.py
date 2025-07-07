import streamlit as st
import pandas as pd
from src.calculators.reaction_calculator import calculate_stoichiometry, calculate_reactor_volume

st.set_page_config(page_title="Reaksiyon Mühendisliği", page_icon="⚛️")

st.title("⚛️ Reaksiyon Mühendisliği")

# Session state'i başlatma
if 'reactants' not in st.session_state:
    st.session_state.reactants = [{'coeff': 2.0, 'name': 'H2', 'moles': 10.0}]
    st.session_state.reactants.append({'coeff': 1.0, 'name': 'O2', 'moles': 10.0})
if 'products' not in st.session_state:
    st.session_state.products = [{'coeff': 2.0, 'name': 'H2O'}]

def add_component(component_type):
    st.session_state[component_type].append({'coeff': 1.0, 'name': '', 'moles': 0.0 if component_type == 'reactants' else None})

def remove_component(component_type, index):
    st.session_state[component_type].pop(index)

st.info("Bu araç, denkleştirilmiş bir reaksiyon için stokiyometrik hesaplamalar yapar. Lütfen reaktifleri ve ürünleri katsayılarıyla birlikte girin.")

# --- Reaksiyon Tanımlama ---
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Reaktifler (Girenler)")
    # Başlıklar
    c1, c2, c3 = st.columns([2, 4, 3])
    c1.write("**Katsayı**")
    c2.write("**Bileşen Adı**")
    c3.write("**Başlangıç Molü**")
    
    for i, r in enumerate(st.session_state.reactants):
        c1, c2, c3, c4 = st.columns([2, 4, 3, 1])
        r['coeff'] = c1.number_input("Katsayı", value=r['coeff'], min_value=0.1, key=f"r_coeff_{i}", label_visibility="collapsed")
        r['name'] = c2.text_input("Bileşen Adı", value=r['name'], key=f"r_name_{i}", label_visibility="collapsed")
        r['moles'] = c3.number_input("Başlangıç Molü", value=r['moles'], min_value=0.0, key=f"r_moles_{i}", label_visibility="collapsed")
        with c4:
            st.write("") # Dikey hizalama için boşluk
            st.button("🗑️", key=f"r_del_{i}", on_click=remove_component, args=('reactants', i), help="Reaktifi sil")
    st.button("➕ Reaktif Ekle", on_click=add_component, args=('reactants',), use_container_width=True)

with col2:
    st.subheader("Ürünler (Çıkanlar)")
    # Başlıklar
    c1, c2 = st.columns([2, 4])
    c1.write("**Katsayı**")
    c2.write("**Bileşen Adı**")

    for i, p in enumerate(st.session_state.products):
        c1, c2, c3 = st.columns([2, 4, 1])
        p['coeff'] = c1.number_input("Katsayı", value=p['coeff'], min_value=0.1, key=f"p_coeff_{i}", label_visibility="collapsed")
        p['name'] = c2.text_input("Bileşen Adı", value=p['name'], key=f"p_name_{i}", label_visibility="collapsed")
        with c3:
            st.write("") # Dikey hizalama için boşluk
            st.button("🗑️", key=f"p_del_{i}", on_click=remove_component, args=('products', i), help="Ürünü sil")
    st.button("➕ Ürün Ekle", on_click=add_component, args=('products',), use_container_width=True)

st.markdown("---")

if st.button("Stokiyometri Hesapla"):
    try:
        # Girdileri hesaplama fonksiyonu için uygun formata getir
        reactants_dict = {r['name']: r['coeff'] for r in st.session_state.reactants if r['name']}
        products_dict = {p['name']: p['coeff'] for p in st.session_state.products if p['name']}
        initial_moles_dict = {r['name']: r['moles'] for r in st.session_state.reactants if r['name']}

        if not reactants_dict:
            st.warning("Lütfen en az bir reaktif girin.")
        else:
            limiting_reactant, final_moles = calculate_stoichiometry(reactants_dict, products_dict, initial_moles_dict)
            
            st.subheader("Stokiyometri Sonuçları")
            st.success(f"**Sınırlayıcı Bileşen:** {limiting_reactant}")
            
            df_data = {
                'Bileşen': [],
                'Başlangıç Mol': [],
                'Son Mol': []
            }
            
            all_components = list(reactants_dict.keys()) + list(products_dict.keys())
            for comp in all_components:
                df_data['Bileşen'].append(comp)
                df_data['Başlangıç Mol'].append(initial_moles_dict.get(comp, 0))
                df_data['Son Mol'].append(final_moles.get(comp, 0))
                
            df = pd.DataFrame(df_data)
            st.dataframe(df.style.format({'Başlangıç Mol': '{:.4f}', 'Son Mol': '{:.4f}'}))

    except Exception as e:
        st.error(f"Hesaplama sırasında bir hata oluştu: {e}")

st.markdown("---")

# --- Reaktör Tasarımı ---
st.subheader("Reaktör Tasarımı (CSTR/PFR)")
st.write("Basit `-rA = k * C_A^n` kinetiği için reaktör hacmini hesaplar.")

reactor_type = st.selectbox("Reaktör Tipi:", ["CSTR", "PFR"])

col1, col2 = st.columns(2)
with col1:
    f_a0 = st.number_input("A'nın Molar Akış Hızı, F_A0 (mol/s)", value=10.0, min_value=0.0)
    c_a0 = st.number_input("A'nın Başlangıç Konsantrasyonu, C_A0 (mol/m³)", value=100.0, min_value=0.0)
    k = st.number_input("Hız Sabiti, k", value=0.1, min_value=0.0, format="%.4f")
with col2:
    X = st.number_input("Hedeflenen Dönüşüm, X", value=0.8, min_value=0.0, max_value=0.999, format="%.3f")
    n = st.number_input("Reaksiyon Mertebesi, n", value=1.0, min_value=0.0, step=0.5)

if st.button("Reaktör Hacmini Hesapla"):
    try:
        volume = calculate_reactor_volume(f_a0, c_a0, k, X, n, reactor_type)
        st.success(f"Gerekli **{reactor_type}** Hacmi: **{volume:,.3f} m³** ({volume*1000:,.2f} L)")
    except Exception as e:
        st.error(f"Hesaplama hatası: {e}")
