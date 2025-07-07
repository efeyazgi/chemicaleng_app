from scipy.integrate import quad

def calculate_stoichiometry(reactants, products, initial_moles):
    """
    Verilen reaksiyon ve başlangıç mollerine göre sınırlayıcı bileşeni,
    kalan molleri ve oluşan ürün mollerini hesaplar.
    """
    if not all(reactant in initial_moles for reactant in reactants.keys()):
        raise ValueError("Tüm reaktifler için başlangıç molü girilmelidir.")

    # Sınırlayıcı bileşeni bulma
    extents = {name: initial_moles[name] / coeff for name, coeff in reactants.items() if coeff > 0}
    if not extents:
        raise ValueError("Reaktiflerin katsayıları pozitif olmalıdır.")
    limiting_reactant = min(extents, key=extents.get)
    reaction_extent = extents[limiting_reactant]

    # Kalan reaktif mollerini hesaplama
    final_moles = {}
    for name, coeff in reactants.items():
        final_moles[name] = initial_moles[name] - reaction_extent * coeff

    # Oluşan ürün mollerini hesaplama
    for name, coeff in products.items():
        final_moles[name] = reaction_extent * coeff
        
    return limiting_reactant, final_moles

def calculate_reactor_volume(F_A0, C_A0, k, X, n, reactor_type):
    """
    Basit bir -rA = k * C_A^n kinetiği için CSTR veya PFR hacmini hesaplar.
    F_A0: A'nın molar akış hızı (mol/s)
    C_A0: A'nın başlangıç konsantrasyonu (mol/m³)
    k: Hız sabiti
    X: Dönüşüm
    n: Reaksiyon mertebesi
    reactor_type: 'CSTR' veya 'PFR'
    """
    if F_A0 <= 0 or C_A0 <= 0 or k <= 0 or not (0 < X < 1):
        raise ValueError("Akış hızı, konsantrasyon, k pozitif olmalı ve dönüşüm 0 ile 1 arasında olmalıdır.")

    # -rA = k * C_A0^n * (1-X)^n
    rate_expression = lambda x: k * (C_A0 * (1 - x))**n
    
    if reactor_type == 'CSTR':
        # V = F_A0 * X / (-rA_exit)
        rate_at_exit = rate_expression(X)
        volume = (F_A0 * X) / rate_at_exit
        return volume

    elif reactor_type == 'PFR':
        # V = F_A0 * integral(dX / -rA) from 0 to X
        integrand = lambda x: 1 / rate_expression(x)
        # integral fonksiyonu, scipy.integrate.quad ile hesaplanır
        integral_val, _ = quad(integrand, 0, X)
        volume = F_A0 * integral_val
        return volume
        
    else:
        raise ValueError("Geçersiz reaktör tipi. 'CSTR' veya 'PFR' seçin.")
