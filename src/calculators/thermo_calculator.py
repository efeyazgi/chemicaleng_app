import pandas as pd
from thermo import Chemical

def calculate_properties(chemical_name, temperature_input, pressure_input, unit_system, selected_properties_keys):
    """
    Verilen kimyasal, sıcaklık, basınç ve birim sistemine göre
    seçilen termodinamik özellikleri hesaplar ve bir DataFrame olarak döndürür.
    """
    property_options = {
        "Yoğunluk (rho)": "rho",
        "Viskozite (mu)": "mu",
        "Isı Kapasitesi (Cp)": "Cp",
        "Buhar Basıncı (Psat)": "Psat",
        "Yüzey Gerilimi (sigma)": "sigma",
        "Isıl İletkenlik (k)": "k",
        "Kaynama Noktası (Tb)": "Tb",
        "Donma Noktası (Tm)": "Tm"
    }
    
    # Girdi birimlerini SI'ya çevirme
    if unit_system == "Metric (CGS)":
        temperature = temperature_input + 273.15  # °C -> K
        pressure = pressure_input * 1e5          # bar -> Pa
    elif unit_system == "English":
        temperature = (temperature_input - 32) * 5/9 + 273.15  # °F -> K
        pressure = pressure_input * 6894.76                    # psia -> Pa
    else: # SI
        temperature = temperature_input
        pressure = pressure_input

    chem = Chemical(chemical_name, T=temperature, P=pressure)
    
    results = []
    for prop_name in selected_properties_keys:
        prop_key = property_options[prop_name]
        value = getattr(chem, prop_key, None)

        if value is not None:
            # Sonuçları seçilen birim sistemine göre formatlama
            unit = ""
            display_value = ""
            if unit_system == "SI":
                if prop_key in ['Tb', 'Tm', 'Tc']: unit = 'K'
                elif prop_key in ['P', 'Pc', 'Psat']: unit = 'Pa'
                elif prop_key == 'rho': unit = 'kg/m³'
                elif prop_key == 'mu': unit = 'Pa·s'
                elif prop_key == 'Cp': unit = 'J/kg·K'
                elif prop_key == 'sigma': unit = 'N/m'
                elif prop_key == 'k': unit = 'W/m·K'
                display_value = f"{value:.4g}"
            elif unit_system == "Metric (CGS)":
                if prop_key in ['Tb', 'Tm', 'Tc']: value -= 273.15; unit = '°C'
                elif prop_key in ['P', 'Pc', 'Psat']: value /= 1e5; unit = 'bar'
                elif prop_key == 'rho': value /= 1000; unit = 'g/cm³'
                elif prop_key == 'mu': value *= 1000; unit = 'cP'
                elif prop_key == 'Cp': value /= 1000; unit = 'kJ/kg·K'
                elif prop_key == 'sigma': value *= 1000; unit = 'mN/m'
                elif prop_key == 'k': unit = 'W/m·K' # Değişmiyor
                display_value = f"{value:.4g}"
            elif unit_system == "English":
                if prop_key in ['Tb', 'Tm', 'Tc']: value = value*9/5 - 459.67; unit = '°F'
                elif prop_key in ['P', 'Pc', 'Psat']: value /= 6894.76; unit = 'psia'
                elif prop_key == 'rho': value /= 16.0185; unit = 'lb/ft³'
                elif prop_key == 'mu': value *= 671.97; unit = 'lb/ft·s'
                elif prop_key == 'Cp': value /= 4184; unit = 'Btu/lb·°F'
                elif prop_key == 'k': value /= 1.73073; unit = 'Btu/hr·ft·°F'
                elif prop_key == 'sigma': value *= 0.0685218; unit = 'lbf/ft'
                display_value = f"{value:.4g}"
            
            results.append({"Özellik": prop_name, "Değer": display_value, "Birim": unit})
        else:
            results.append({"Özellik": prop_name, "Değer": "Hesaplanamadı", "Birim": "-"})
    
    return pd.DataFrame(results), chem.formula

def generate_plot_data(chemical_name, pressure_input, unit_system, prop_key, temp_min, temp_max):
    """
    Belirli bir özellik için sıcaklığa karşı bir veri seti oluşturur.
    """
    temps = pd.to_numeric(pd.Series(range(int(temp_min), int(temp_max), 5)))
    
    # Girdi birimlerini SI'ya çevirme
    if unit_system == "Metric (CGS)":
        temps_si = temps + 273.15
        pressure = pressure_input * 1e5
    elif unit_system == "English":
        temps_si = (temps - 32) * 5/9 + 273.15
        pressure = pressure_input * 6894.76
    else: # SI
        temps_si = temps
        pressure = pressure_input

    prop_values = []
    for t in temps_si:
        try:
            chem = Chemical(chemical_name, T=t, P=pressure)
            value = getattr(chem, prop_key, None)
            prop_values.append(value)
        except:
            prop_values.append(None)

    df = pd.DataFrame({
        'Sıcaklık': temps,
        'Özellik': prop_values
    })
    df = df.dropna()
    return df
