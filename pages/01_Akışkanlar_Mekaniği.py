import streamlit as st
from src.calculators.fluids_calculator import calculate_reynolds, calculate_pressure_drop
from src.calculators.thermo_calculator import calculate_properties as calculate_thermo_properties

st.set_page_config(page_title="Akışkanlar Mekaniği", page_icon="💧")

# Session state'i başlatma
if 'density' not in st.session_state:
    st.session_state.density = 1000.0
if 'viscosity' not in st.session_state:
    st.session_state.viscosity = 0.001

st.title("💧 Akışkanlar Mekaniği")

# --- Akışkan Özellikleri ---
with st.expander("Akışkan Özelliklerini Hesapla veya Manuel Gir", expanded=True):
    st.write("Burada bir akışkan seçip özelliklerini hesaplatabilir veya aşağıdaki alanlara manuel olarak girebilirsiniz.")
    
    # Sık kullanılan akışkanlar listesi
    common_chemicals = [
        "water", "ethanol", "methanol", "benzene", "toluene",
        "acetone", "ammonia", "carbon dioxide", "oxygen",
        "nitrogen", "air", "methane", "propane", "butane"
    ]
    chemical_name = st.selectbox("Akışkan Seç:", options=common_chemicals)
    
    col1, col2 = st.columns(2)
    with col1:
        temp = st.number_input("Sıcaklık (K)", value=298.15)
    with col2:
        pressure = st.number_input("Basınç (Pa)", value=101325.0)
        
    if st.button("Akışkan Özelliklerini Getir"):
        try:
            df, _ = calculate_thermo_properties(
                chemical_name, temp, pressure, "SI", ["Yoğunluk (rho)", "Viskozite (mu)"]
            )
            # Değerleri string'den float'a çevir
            rho_val = float(df.loc[df['Özellik'] == 'Yoğunluk (rho)', 'Değer'].iloc[0])
            mu_val = float(df.loc[df['Özellik'] == 'Viskozite (mu)', 'Değer'].iloc[0])
            
            st.session_state.density = rho_val
            st.session_state.viscosity = mu_val
            st.success(f"{chemical_name.title()} için özellikler getirildi: Yoğunluk={rho_val:.2f} kg/m³, Viskozite={mu_val:.6f} Pa.s")
        except Exception as e:
            st.error(f"Özellikler getirilemedi: {e}")

st.subheader("Akışkan ve Boru Bilgileri")

# Girdiler
density = st.number_input("Yoğunluk (kg/m³)", value=st.session_state.density, format="%.2f", key="density_input")
velocity = st.number_input("Hız (m/s)", value=1.0, format="%.2f")
diameter = st.number_input("Boru İç Çapı (m)", value=0.1, format="%.3f")
viscosity = st.number_input("Viskozite (Pa.s)", value=st.session_state.viscosity, format="%.6f", key="viscosity_input")

st.divider()

st.subheader("Hesaplamalar")
length = st.number_input("Boru Uzunluğu (m)", value=100.0, format="%.2f")
roughness = st.number_input("Boru Pürüzlülüğü (m)", value=0.000045, format="%.6f", help="Ticari çelik için tipik değer: 0.000045 m")

if st.button("Tüm Hesaplamaları Yap"):
    # Reynolds Hesaplama
    reynolds_number, flow_type, re_error = calculate_reynolds(st.session_state.density, velocity, diameter, st.session_state.viscosity)
    
    if re_error:
        st.error(f"Reynolds Hatası: {re_error}")
    else:
        st.write("---")
        st.subheader("Sonuçlar")
        st.markdown(f"**Reynolds Sayısı (Re):** `{reynolds_number:,.2f}`")
        
        if flow_type == "Laminer":
            st.info(f"**Akış Tipi:** {flow_type} (Re < 2300)")
        elif flow_type == "Geçiş Bölgesi":
            st.warning(f"**Akış Tipi:** {flow_type} (2300 ≤ Re ≤ 4000)")
        else:
            st.error(f"**Akış Tipi:** {flow_type} (Re > 4000)")
        
        # Basınç Düşüşü Hesaplama
        pressure_drop, friction_factor, pd_error = calculate_pressure_drop(
            st.session_state.density, velocity, diameter, st.session_state.viscosity, length, roughness
        )
        
        if pd_error:
            st.error(f"Basınç Düşüşü Hatası: {pd_error}")
        else:
            st.markdown(f"**Darcy Sürtünme Faktörü (fD):** `{friction_factor:.4f}`")
            st.markdown(f"**Basınç Düşüşü (ΔP):** `{pressure_drop:,.2f} Pa` ({pressure_drop/1e5:,.4f} bar)")
