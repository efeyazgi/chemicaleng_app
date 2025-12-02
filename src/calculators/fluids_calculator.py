from fluids.friction import friction_factor

def calculate_reynolds(density, velocity, diameter, viscosity):
    """
    Verilen parametrelerle Reynolds sayısını ve akış tipini hesaplar.
    """
    # Fiziksel kısıtlamalar:
    # Yoğunluk > 0, Çap > 0, Viskozite > 0 (bölme hatası olmaması için)
    # Hız >= 0 olabilir (akış yoksa Re=0)
    if density <= 0:
        return None, None, "Yoğunluk sıfırdan büyük olmalıdır."
    if diameter <= 0:
        return None, None, "Çap sıfırdan büyük olmalıdır."
    if viscosity <= 0:
        return None, None, "Viskozite sıfırdan büyük olmalıdır."
    if velocity < 0:
        return None, None, "Hız negatif olamaz."

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
    
    if length <= 0:
        return None, None, "Uzunluk sıfırdan büyük olmalıdır."
    if roughness < 0:
        return None, None, "Pürüzlülük negatif olamaz."

    # Sürtünme faktörünü hesapla
    try:
        fd = friction_factor(Re=re, eD=roughness/diameter)
    except Exception as e:
        return None, None, f"Sürtünme faktörü hesaplanırken hata: {str(e)}"
    
    # Basınç düşüşünü hesapla (Pa)
    pressure_drop = fd * (length / diameter) * (density * velocity**2) / 2
    
    return pressure_drop, fd, None
