import streamlit as st
from pint import UnitRegistry

ureg = UnitRegistry()

def convert_value(value, from_unit, to_unit):
    """
    Değeri bir birimden diğerine çevirir.
    """
    try:
        # Pint ile çevirim
        # String temizliği gerekebilir (örn: m**3 -> m^3) ama Pint ** destekler.
        return ureg.Quantity(value, from_unit).to(to_unit).magnitude
    except Exception as e:
        # st.error(f"Birim çevirme hatası ({from_unit} -> {to_unit}): {e}")
        return value


# Görüntüleme için özel haritalama (Pint birimi -> Görüntülenen birim)
UNIT_DISPLAY_MAP = {
    "degC": "°C", "degF": "°F", "degR": "°R",
    "m**3": "m³", "ft**3": "ft³", "cm**3": "cm³",
    "kg/m**3": "kg/m³", "g/cm**3": "g/cm³", "lb/ft**3": "lb/ft³",
    "m/s": "m/s", "ft/s": "ft/s",
    "Pa*s": "Pa·s", "mPa*s": "mPa·s",
    "J/(kg*K)": "J/(kg·K)", "kJ/(kg*K)": "kJ/(kg·K)", "Btu/(lb*degF)": "Btu/(lb·°F)",
    "W/(m*K)": "W/(m·K)", "Btu/(hr*ft*degF)": "Btu/(hr·ft·°F)",
    "mol/m**3": "mol/m³", "kmol/m**3": "kmol/m³", "lbmol/ft**3": "lbmol/ft³",
    "mol/(m**3*s)": "mol/(m³·s)",
    "J/mol": "J/mol", "kJ/mol": "kJ/mol"
}

def format_unit(unit_str):
    """Birimi kullanıcı dostu formata çevirir."""
    return UNIT_DISPLAY_MAP.get(unit_str, unit_str)

# Standart Birim Sistemleri Tanımları
UNIT_SYSTEMS = {
    "SI": {
        "T": "K", "P": "Pa", "Flow": "mol/s", "Vol": "m**3", "Len": "m", "Mass": "kg", "Time": "s",
        "Density": "kg/m**3", "Viscosity": "Pa*s", "Energy": "J", 
        "Cp": "J/(kg*K)", "ThermalCond": "W/(m*K)", "SurfaceTension": "N/m",
        "Conc": "mol/m**3", "Rate": "mol/(m**3*s)", "ActivationEnergy": "J/mol",
        "Velocity": "m/s"
    },
    "Metric": {
        "T": "degC", "P": "bar", "Flow": "kmol/hr", "Vol": "L", "Len": "cm", "Mass": "kg", "Time": "hr",
        "Density": "g/cm**3", "Viscosity": "cP", "Energy": "kJ", 
        "Cp": "kJ/(kg*K)", "ThermalCond": "W/(m*K)", "SurfaceTension": "mN/m",
        "Conc": "kmol/m**3", "Rate": "kmol/(m**3*hr)", "ActivationEnergy": "kJ/mol",
        "Velocity": "m/s"
    },
    "English": {
        "T": "degF", "P": "psi", "Flow": "lbmol/hr", "Vol": "ft**3", "Len": "ft", "Mass": "lb", "Time": "hr",
        "Density": "lb/ft**3", "Viscosity": "lb/(ft*s)", "Energy": "Btu", 
        "Cp": "Btu/(lb*degF)", "ThermalCond": "Btu/(hr*ft*degF)", "SurfaceTension": "lbf/ft",
        "Conc": "lbmol/ft**3", "Rate": "lbmol/(ft**3*hr)", "ActivationEnergy": "Btu/lbmol",
        "Velocity": "ft/s"
    }
}

UNIT_OPTIONS = {
    "T": ["K", "degC", "degF", "degR"],
    "P": ["Pa", "bar", "atm", "psi", "mmHg", "kPa", "MPa", "torr"],
    "Flow": ["mol/s", "kmol/hr", "lbmol/hr", "mol/min"],
    "Vol": ["m**3", "L", "ft**3", "gal", "mL"],
    "Len": ["m", "cm", "mm", "ft", "in"],
    "Mass": ["kg", "g", "lb", "oz", "ton"],
    "Time": ["s", "min", "hr", "day"],
    "Density": ["kg/m**3", "g/cm**3", "lb/ft**3", "kg/L", "g/mL"],
    "Viscosity": ["Pa*s", "cP", "P", "lb/(ft*s)", "mPa*s"],
    "Energy": ["J", "kJ", "cal", "kcal", "Btu"],
    "Cp": ["J/(kg*K)", "kJ/(kg*K)", "cal/(g*degC)", "Btu/(lb*degF)", "kcal/(kg*degC)"],
    "ThermalCond": ["W/(m*K)", "Btu/(hr*ft*degF)", "cal/(s*cm*degC)", "mW/(m*K)"],
    "SurfaceTension": ["N/m", "mN/m", "dyne/cm", "lbf/ft"],
    "Conc": ["mol/m**3", "kmol/m**3", "mol/L", "lbmol/ft**3", "g/L"],
    "Rate": ["mol/(m**3*s)", "kmol/(m**3*hr)", "mol/(L*s)", "lbmol/(ft**3*hr)"],
    "ActivationEnergy": ["J/mol", "kJ/mol", "cal/mol", "kcal/mol", "Btu/lbmol"],
    "Velocity": ["m/s", "km/hr", "ft/s", "mph"]
}

def init_unit_state():
    """Session state başlatma."""
    if 'global_unit_system' not in st.session_state:
        st.session_state['global_unit_system'] = "SI"
    
    if 'custom_units' not in st.session_state:
        st.session_state['custom_units'] = UNIT_SYSTEMS["SI"].copy()

def render_global_settings_sidebar():
    """Sidebar'da genel ayarları gösterir."""
    init_unit_state()
    
    st.sidebar.markdown("### 🌐 Genel Ayarlar")
    
    # Sistem Seçimi
    current_sys = st.session_state['global_unit_system']
    
    # Selectbox key'i unique olmalı
    selected_sys = st.sidebar.selectbox(
        "Varsayılan Birim Sistemi",
        options=["SI", "Metric", "English", "Manual"],
        index=["SI", "Metric", "English", "Manual"].index(current_sys),
        key="global_unit_selector_sidebar"
    )
    
    # Değişiklik varsa kaydet
    if selected_sys != current_sys:
        st.session_state['global_unit_system'] = selected_sys
        # Hazır sistem seçildiyse custom_units'i güncelle (başlangıç noktası olarak)
        if selected_sys in UNIT_SYSTEMS:
            st.session_state['custom_units'] = UNIT_SYSTEMS[selected_sys].copy()
        st.rerun()

    # Manual seçiliyse detayları göster
    if selected_sys == "Manual":
        with st.sidebar.expander("🛠️ Birimleri Özelleştir"):
            for dim, options in UNIT_OPTIONS.items():
                current_unit = st.session_state['custom_units'].get(dim, options[0])
                if current_unit not in options:
                    options = [current_unit] + options
                
                new_unit = st.selectbox(
                    f"{dim} Birimi", 
                    options, 
                    index=options.index(current_unit),
                    key=f"global_manual_{dim}",
                    format_func=format_unit
                )
                st.session_state['custom_units'][dim] = new_unit

def render_local_unit_override(module_key):
    """
    Modül içinde yerel birim ayarlarını gösterir.
    Global ayarı varsayılan olarak kullanır ama override edilebilir.
    """
    init_unit_state()
    
    # Local state key
    local_sys_key = f"{module_key}_unit_system"
    
    # Eğer local state henüz yoksa globalden al
    if local_sys_key not in st.session_state:
        st.session_state[local_sys_key] = st.session_state['global_unit_system']
        
    # UI
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("") # Spacer
    with col2:
        # Küçük bir ayar butonu veya selectbox
        # Kullanıcı "Modül Ayarları" gibi bir expander içinde de görebilir
        pass

    # Daha belirgin bir yerleşim:
    with st.expander("⚙️ Birim Ayarları", expanded=False):
        current_local = st.session_state[local_sys_key]
        
        selected_local = st.selectbox(
            "Bu Modül İçin Birim Sistemi",
            options=["Global Ayarı Kullan", "SI", "Metric", "English", "Manual"],
            index=0 if current_local == st.session_state['global_unit_system'] else ["SI", "Metric", "English", "Manual"].index(current_local) + 1 if current_local in ["SI", "Metric", "English", "Manual"] else 4,
            key=f"{module_key}_selector"
        )
        
        if selected_local == "Global Ayarı Kullan":
            effective_sys = st.session_state['global_unit_system']
            st.session_state[local_sys_key] = effective_sys
        else:
            effective_sys = selected_local
            st.session_state[local_sys_key] = effective_sys
            
        # Manual override for this module
        effective_units = {}
        if effective_sys == "Manual":
            # Local manual units
            local_manual_key = f"{module_key}_manual_units"
            if local_manual_key not in st.session_state:
                # Copy from global custom units as base
                st.session_state[local_manual_key] = st.session_state['custom_units'].copy()
            
            st.markdown("#### Özel Birimler")
            cols = st.columns(2)
            for i, (dim, options) in enumerate(UNIT_OPTIONS.items()):
                with cols[i % 2]:
                    current_u = st.session_state[local_manual_key].get(dim, options[0])
                    if current_u not in options: options = [current_u] + options
                    
                    new_u = st.selectbox(
                        f"{dim}", 
                        options, 
                        index=options.index(current_u),
                        key=f"{module_key}_manual_{dim}",
                        format_func=format_unit
                    )
                    st.session_state[local_manual_key][dim] = new_u
            
            effective_units = st.session_state[local_manual_key]
        elif effective_sys in UNIT_SYSTEMS:
            effective_units = UNIT_SYSTEMS[effective_sys]
        else:
            # Fallback
            effective_units = UNIT_SYSTEMS["SI"]
            
    return effective_sys, effective_units

def get_active_units(module_key):
    """
    Aktif birim sözlüğünü döndürür.
    """
    init_unit_state()
    local_sys_key = f"{module_key}_unit_system"
    
    # Determine system
    sys_name = st.session_state.get(local_sys_key, st.session_state['global_unit_system'])
    
    if sys_name == "Manual":
        local_manual_key = f"{module_key}_manual_units"
        if local_manual_key in st.session_state:
            return st.session_state[local_manual_key]
        return st.session_state['custom_units']
    
    return UNIT_SYSTEMS.get(sys_name, UNIT_SYSTEMS["SI"])
