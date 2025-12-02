import pandas as pd
from thermo import Chemical
from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

# Yaygın kimyasallar ve Türkçe karşılıkları
CHEMICAL_TRANSLATIONS = {
    "water": "Su (Water)",
    "ethanol": "Etanol (Ethanol)",
    "methanol": "Metanol (Methanol)",
    "benzene": "Benzen (Benzene)",
    "toluene": "Toluen (Toluene)",
    "acetone": "Aseton (Acetone)",
    "ammonia": "Amonyak (Ammonia)",
    "carbon dioxide": "Karbondioksit (Carbon Dioxide)",
    "oxygen": "Oksijen (Oxygen)",
    "nitrogen": "Azot (Nitrogen)",
    "air": "Hava (Air)",
    "methane": "Metan (Methane)",
    "propane": "Propan (Propane)",
    "butane": "Butan (Butane)",
    "pentane": "Pentan (Pentane)",
    "hexane": "Heksan (Hexane)",
    "heptane": "Heptan (Heptane)",
    "octane": "Oktan (Octane)",
    "ethylene": "Etilen (Ethylene)",
    "propylene": "Propilen (Propylene)",
    "sulfuric acid": "Sülfürik Asit (Sulfuric Acid)",
    "hydrochloric acid": "Hidroklorik Asit (Hydrochloric Acid)",
    "nitric acid": "Nitrik Asit (Nitric Acid)",
    "acetic acid": "Asetik Asit (Acetic Acid)",
    "chloroform": "Kloroform (Chloroform)",
    "carbon tetrachloride": "Karbon Tetraklorür (Carbon Tetrachloride)",
    "diethyl ether": "Dietil Eter (Diethyl Ether)",
    "glycerol": "Gliserol (Glycerol)",
    "hydrogen": "Hidrojen (Hydrogen)",
    "helium": "Helyum (Helium)",
    "argon": "Argon (Argon)",
    "chlorine": "Klor (Chlorine)",
    "sulfur dioxide": "Kükürt Dioksit (Sulfur Dioxide)",
}

def get_chemical_list():
    """Kimyasal listesini (İngilizce Key, Türkçe Value) döndürür."""
    return CHEMICAL_TRANSLATIONS

def calculate_properties(chemical_name, temperature_input, pressure_input, unit_system, selected_properties_keys, manual_units=None):
    """
    Verilen kimyasal, sıcaklık, basınç ve birim sistemine göre
    seçilen termodinamik özellikleri hesaplar ve bir DataFrame olarak döndürür.
    
    manual_units: {'T': 'degC', 'P': 'bar', 'rho': 'kg/m**3', ...} gibi sözlük
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
    
    # Girdi birimlerini SI'ya (Kelvin, Pascal) çevirme
    try:
        if unit_system == "Metric (CGS)":
            T_si = Q_(temperature_input, "degC").to("kelvin").magnitude
            P_si = Q_(pressure_input, "bar").to("pascal").magnitude
        elif unit_system == "English":
            T_si = Q_(temperature_input, "degF").to("kelvin").magnitude
            P_si = Q_(pressure_input, "psi").to("pascal").magnitude
        elif unit_system == "Manual" and manual_units:
            T_si = Q_(temperature_input, manual_units.get('T', 'kelvin')).to("kelvin").magnitude
            P_si = Q_(pressure_input, manual_units.get('P', 'pascal')).to("pascal").magnitude
        else: # SI
            T_si = temperature_input
            P_si = pressure_input
    except Exception as e:
        return pd.DataFrame([{"Özellik": "Hata", "Değer": f"Birim çevirme hatası: {e}", "Birim": "-"}]), ""

    if T_si <= 0:
        return pd.DataFrame([{"Özellik": "Hata", "Değer": "Sıcaklık 0 Kelvin'den büyük olmalıdır.", "Birim": "-"}]), ""
    if P_si <= 0:
        return pd.DataFrame([{"Özellik": "Hata", "Değer": "Basınç 0 Pascal'dan büyük olmalıdır.", "Birim": "-"}]), ""

    try:
        chem = Chemical(chemical_name, T=T_si, P=P_si)
    except Exception as e:
        return pd.DataFrame([{"Özellik": "Hata", "Değer": f"Kimyasal bulunamadı veya hata: {str(e)}", "Birim": "-"}]), ""
    
    results = []
    for prop_name in selected_properties_keys:
        prop_key = property_options[prop_name]
        value = getattr(chem, prop_key, None)

        if value is not None:
            # SI değerleri (thermo kütüphanesi SI döner)
            # rho: kg/m3, mu: Pa*s, Cp: J/kg/K, Psat: Pa, sigma: N/m, k: W/m/K, Tb: K, Tm: K
            
            unit_str = ""
            display_value = ""
            
            try:
                # Hedef birime çevirme
                if unit_system == "SI":
                    if prop_key in ['Tb', 'Tm']: unit_str = 'K'
                    elif prop_key in ['Psat']: unit_str = 'Pa'
                    elif prop_key == 'rho': unit_str = 'kg/m³'
                    elif prop_key == 'mu': unit_str = 'Pa·s'
                    elif prop_key == 'Cp': unit_str = 'J/(kg·K)'
                    elif prop_key == 'sigma': unit_str = 'N/m'
                    elif prop_key == 'k': unit_str = 'W/(m·K)'
                    val_conv = value
                    
                elif unit_system == "Metric (CGS)":
                    if prop_key in ['Tb', 'Tm']: 
                        val_conv = Q_(value, 'kelvin').to('degC').magnitude; unit_str = '°C'
                    elif prop_key in ['Psat']: 
                        val_conv = Q_(value, 'pascal').to('bar').magnitude; unit_str = 'bar'
                    elif prop_key == 'rho': 
                        val_conv = Q_(value, 'kg/m**3').to('g/cm**3').magnitude; unit_str = 'g/cm³'
                    elif prop_key == 'mu': 
                        val_conv = Q_(value, 'pascal*second').to('centipoise').magnitude; unit_str = 'cP'
                    elif prop_key == 'Cp': 
                        val_conv = Q_(value, 'joule/(kg*kelvin)').to('kJ/(kg*kelvin)').magnitude; unit_str = 'kJ/(kg·K)'
                    elif prop_key == 'sigma': 
                        val_conv = Q_(value, 'newton/meter').to('millinewton/meter').magnitude; unit_str = 'mN/m'
                    elif prop_key == 'k': 
                        val_conv = value; unit_str = 'W/(m·K)'

                elif unit_system == "English":
                    if prop_key in ['Tb', 'Tm']: 
                        val_conv = Q_(value, 'kelvin').to('degF').magnitude; unit_str = '°F'
                    elif prop_key in ['Psat']: 
                        val_conv = Q_(value, 'pascal').to('psi').magnitude; unit_str = 'psia'
                    elif prop_key == 'rho': 
                        val_conv = Q_(value, 'kg/m**3').to('lb/ft**3').magnitude; unit_str = 'lb/ft³'
                    elif prop_key == 'mu': 
                        val_conv = Q_(value, 'pascal*second').to('lb/(ft*s)').magnitude; unit_str = 'lb/(ft·s)'
                    elif prop_key == 'Cp': 
                        val_conv = Q_(value, 'joule/(kg*kelvin)').to('btu/(lb*degF)').magnitude; unit_str = 'Btu/(lb·°F)'
                    elif prop_key == 'sigma': 
                        val_conv = Q_(value, 'newton/meter').to('lbf/ft').magnitude; unit_str = 'lbf/ft'
                    elif prop_key == 'k': 
                        val_conv = Q_(value, 'watt/(meter*kelvin)').to('btu/(hour*ft*degF)').magnitude; unit_str = 'Btu/(hr·ft·°F)'
                
                elif unit_system == "Manual" and manual_units:
                    # Manuel çevirim
                    target_unit = manual_units.get(prop_key, None)
                    if target_unit:
                        # Kaynak birimler (SI)
                        src_units = {
                            'rho': 'kg/m**3', 'mu': 'pascal*second', 'Cp': 'joule/(kg*kelvin)',
                            'Psat': 'pascal', 'sigma': 'newton/meter', 'k': 'watt/(meter*kelvin)',
                            'Tb': 'kelvin', 'Tm': 'kelvin'
                        }
                        src = src_units.get(prop_key)
                        if src:
                            val_conv = Q_(value, src).to(target_unit).magnitude
                            unit_str = target_unit
                        else:
                            val_conv = value; unit_str = "-"
                    else:
                        val_conv = value; unit_str = "(SI)"
                
                else:
                    val_conv = value; unit_str = "-"

                display_value = f"{val_conv:.4g}"
            except Exception as e:
                display_value = "Çevrim Hatası"
                unit_str = str(e)

            results.append({"Özellik": prop_name, "Değer": display_value, "Birim": unit_str})
        else:
            results.append({"Özellik": prop_name, "Değer": "Hesaplanamadı", "Birim": "-"})
    
    return pd.DataFrame(results), chem.formula

def generate_plot_data(chemical_name, pressure_input, unit_system, prop_key, temp_min, temp_max, manual_units=None):
    """
    Belirli bir özellik için sıcaklığa karşı bir veri seti oluşturur.
    """
    if temp_min >= temp_max:
         return pd.DataFrame() 

    temps = pd.to_numeric(pd.Series(range(int(temp_min), int(temp_max), 5)))
    
    # Basınç ve Sıcaklık SI (Pa, K) dönüşümü
    if unit_system == "Metric (CGS)":
        P_si = Q_(pressure_input, "bar").to("pascal").magnitude
        temps_k = Q_(temps.values, "degC").to("kelvin").magnitude
    elif unit_system == "English":
        P_si = Q_(pressure_input, "psi").to("pascal").magnitude
        temps_k = Q_(temps.values, "degF").to("kelvin").magnitude
    elif unit_system == "Manual" and manual_units:
        P_si = Q_(pressure_input, manual_units.get('P', 'pascal')).to("pascal").magnitude
        t_unit = manual_units.get('T', 'kelvin')
        temps_k = Q_(temps.values, t_unit).to("kelvin").magnitude
    else: # SI
        P_si = pressure_input
        temps_k = temps.values

    prop_values = []
    for t_k in temps_k:
        try:
            if t_k <= 0: 
                prop_values.append(None)
                continue
            chem = Chemical(chemical_name, T=t_k, P=P_si)
            value = getattr(chem, prop_key, None)
            
            # Değeri grafikte gösterilecek birime çevir (Manuel birim seçildiyse)
            if value is not None and unit_system == "Manual" and manual_units:
                 target_unit = manual_units.get(prop_key)
                 if target_unit:
                     src_units = {
                        'rho': 'kg/m**3', 'mu': 'pascal*second', 'Cp': 'joule/(kg*kelvin)',
                        'Psat': 'pascal', 'sigma': 'newton/meter', 'k': 'watt/(meter*kelvin)',
                        'Tb': 'kelvin', 'Tm': 'kelvin'
                     }
                     src = src_units.get(prop_key)
                     if src:
                         value = Q_(value, src).to(target_unit).magnitude

            prop_values.append(value)
        except Exception as e:
            # Hata durumunda None ekle ama hatayı da görebilmek için print edebiliriz
            print(f"Error for T={t_k}: {e}")
            prop_values.append(None)

    df = pd.DataFrame({
        'Sıcaklık': temps,
        'Özellik': prop_values
    })
    df = df.dropna()
    return df
