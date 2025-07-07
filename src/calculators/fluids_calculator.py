from fluids.friction import friction_factor

def calculate_reynolds(density, velocity, diameter, viscosity):
    """
    Verilen parametrelerle Reynolds sayısını ve akış tipini hesaplar.
    """
    if any(v <= 0 for v in [density, velocity, diameter, viscosity]):
        return None, None, "Tüm değerler sıfırdan büyük olmalıdır."

    reynolds_number = (density * velocity * diameter) / viscosity
    
    if reynolds_number < 2300:
        flow_type = "Laminer"
    elif 2300 <= reynolds_number <= 4000:
        flow_type = "Geçiş Bölgesi"
    else:
        flow_type = "Türbülanslı"
        
    return reynolds_number, flow_type, None

def calculate_pressure_drop(density, velocity, diameter, viscosity, length, roughness):
    """
    Darcy-Weisbach denklemini kullanarak basınç düşüşünü hesaplar.
    """
    re, _, error = calculate_reynolds(density, velocity, diameter, viscosity)
    if error:
        return None, None, error
    
    if length <= 0 or roughness < 0:
        return None, None, "Uzunluk pozitif, pürüzlülük pozitif veya sıfır olmalıdır."

    # Sürtünme faktörünü hesapla
    fd = friction_factor(Re=re, eD=roughness/diameter)
    
    # Basınç düşüşünü hesapla (Pa)
    pressure_drop = fd * (length / diameter) * (density * velocity**2) / 2
    
    return pressure_drop, fd, None
