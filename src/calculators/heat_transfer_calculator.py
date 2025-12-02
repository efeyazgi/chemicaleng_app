import math
from scipy.integrate import quad
from pint import UnitRegistry

# Birim sistemi
ureg = UnitRegistry()
Q_ = ureg.Quantity

# Material library example (conductivity in W/m·K)
MATERIAL_LIBRARY = {
    'Copper': 401.0,
    'Steel': 50.2,
    'Concrete': 1.7,
    'Glass': 1.05
}

# --- Düzlem Duvar ---
def calculate_planar_wall_heat_transfer(t_inner, h_inner, t_outer, h_outer, area, layers):
    """
    Düzlem duvardan ısı transferi.
    layers: her biri {'thickness': L (m), 'conductivity': k (W/m·K)}
    Dönen: q [W], r_total [K/W]
    """
    if area <= 0:
        return None, None, "Alan sıfırdan büyük olmalıdır."
    if h_inner <= 0 or h_outer <= 0:
        return None, None, "Isı taşınım katsayıları (h) sıfırdan büyük olmalıdır."
        
    # Konveksiyon
    r_conv_i = 1/(h_inner * area)
    r_conv_o = 1/(h_outer * area)
    # Kondüksiyon
    r_cond_list = []
    for ly in layers:
        L = ly['thickness']; k = ly['conductivity']
        if L < 0:
            return None, None, "Katman kalınlığı negatif olamaz."
        if k <= 0:
            return None, None, "Isıl iletkenlik sıfırdan büyük olmalıdır."
        r_cond_list.append(L/(k*area))
    r_total = r_conv_i + sum(r_cond_list) + r_conv_o
    q = (t_inner - t_outer)/r_total
    return Q_(q, 'watt'), Q_(r_total, 'kelvin/ watt'), None


def compute_planar_temperature_profile(t_inner, h_inner, t_outer, h_outer, area, layers):
    """
    Düzlem duvar sıcaklık profili (pozisyon (m) vs sıcaklık (K)).
    Dönen: positions, temps, error
    """
    result = calculate_planar_wall_heat_transfer(t_inner, h_inner, t_outer, h_outer, area, layers)
    if result[2] is not None:
        return None, None, result[2]
    q, r_total, _ = result
    # Konveksiyon ve kondüksiyon dirençleri
    r_conv_i = 1/(h_inner * area)
    r_conv_o = 1/(h_outer * area)
    r_cond_list = [ly['thickness']/(ly['conductivity']*area) for ly in layers]
    resistances = [r_conv_i] + r_cond_list + [r_conv_o]
    # Orijinal pozisyon listesi (katman ara yüzeyleri)
    pos = [0]
    for ly in layers:
        pos.append(pos[-1] + ly['thickness'])
    total_thickness = pos[-1]
    # Genişletilmiş pozisyonlar: iç film, katman ara yüzeyleri, dış film
    positions = [0, 0] + pos[1:] + [total_thickness]
    # Sıcaklık düşüşü hesaplaması
    temps = [t_inner]
    for r in resistances:
        delta_T = q.magnitude * r
        temps.append(temps[-1] - delta_T)
    return positions, temps, None

# --- Silindirik Kabuk ---
def calculate_cylindrical_shell_heat_transfer(t_inner, h_inner, t_outer, h_outer, length, r_inner, r_outer, conductivity):
    """
    Silindirik kabuktan ısı transferi.
    Dönen: q [W], r_total [K/W]
    """
    if length <= 0:
        return None, None, "Uzunluk sıfırdan büyük olmalıdır."
    if r_inner <= 0 or r_outer <= 0:
        return None, None, "Yarıçaplar sıfırdan büyük olmalıdır."
    if r_outer <= r_inner:
        return None, None, "Dış yarıçap iç yarıçaptan büyük olmalıdır."
    if conductivity <= 0:
        return None, None, "Isıl iletkenlik sıfırdan büyük olmalıdır."
    if h_inner <= 0 or h_outer <= 0:
        return None, None, "Isı taşınım katsayıları (h) sıfırdan büyük olmalıdır."

    A_i = 2*math.pi*r_inner*length
    A_o = 2*math.pi*r_outer*length
    r_conv_i = 1/(h_inner * A_i)
    r_conv_o = 1/(h_outer * A_o)
    
    r_cond = math.log(r_outer/r_inner)/(2*math.pi*conductivity*length)
    r_total = r_conv_i + r_cond + r_conv_o
    q = (t_inner - t_outer)/r_total
    return Q_(q, 'watt'), Q_(r_total, 'kelvin/ watt'), None

# --- Küresel Kabuk ---
def calculate_spherical_shell_heat_transfer(t_inner, h_inner, t_outer, h_outer, r_inner, r_outer, conductivity):
    """
    Küresel kabuktan ısı transferi.
    Dönen: q [W], r_total [K/W]
    """
    if r_inner <= 0 or r_outer <= 0:
        return None, None, "Yarıçaplar sıfırdan büyük olmalıdır."
    if r_outer <= r_inner:
        return None, None, "Dış yarıçap iç yarıçaptan büyük olmalıdır."
    if conductivity <= 0:
        return None, None, "Isıl iletkenlik sıfırdan büyük olmalıdır."
    if h_inner <= 0 or h_outer <= 0:
        return None, None, "Isı taşınım katsayıları (h) sıfırdan büyük olmalıdır."

    A_i = 4*math.pi*r_inner**2
    A_o = 4*math.pi*r_outer**2
    r_conv_i = 1/(h_inner * A_i)
    r_conv_o = 1/(h_outer * A_o)
    
    r_cond = (1/(4*math.pi*conductivity))*(1/r_inner - 1/r_outer)
    r_total = r_conv_i + r_cond + r_conv_o
    q = (t_inner - t_outer)/r_total
    return Q_(q, 'watt'), Q_(r_total, 'kelvin/ watt'), None