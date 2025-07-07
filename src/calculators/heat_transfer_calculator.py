def calculate_planar_wall_heat_transfer(t_inner, h_inner, t_outer, h_outer, area, layers):
    """
    Konveksiyon ve kondüksiyon dahil olmak üzere düzlem bir duvardan
    toplam ısı transfer hızını hesaplar.
    
    layers: [{'thickness': L, 'conductivity': k}, ...] formatında bir liste
    """
    if area <= 0:
        return None, None, "Alan sıfırdan büyük olmalıdır."

    # İç ve dış konveksiyon dirençleri
    r_conv_inner = 1 / (h_inner * area)
    r_conv_outer = 1 / (h_outer * area)
    
    # Katmanların kondüksiyon dirençleri
    r_cond_total = 0
    for layer in layers:
        thickness = layer['thickness']
        conductivity = layer['conductivity']
        if thickness < 0 or conductivity <= 0:
            return None, None, "Katman kalınlığı negatif olamaz ve ısıl iletkenlik pozitif olmalıdır."
        r_cond_total += thickness / (conductivity * area)
        
    # Toplam direnç
    r_total = r_conv_inner + r_cond_total + r_conv_outer
    
    # Toplam ısı transfer hızı
    q = (t_inner - t_outer) / r_total
    
    return q, r_total, None
