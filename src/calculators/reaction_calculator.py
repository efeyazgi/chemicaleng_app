import math
import numpy as np
import pandas as pd
from scipy.integrate import quad
from pint import UnitRegistry

# Birim sistemi - Tek bir registry örneği
ureg = UnitRegistry()
Q_ = ureg.Quantity

def _k_units_for_order(overall_order: float) -> str:
    """Toplam mertebeye göre hız sabiti birimini döndürür."""
    if abs(overall_order - 1.0) < 1e-12:
        return '1/second'
    
    # [k] = (conc)^(1-n) / time = (mol/m^3)^(1-n) / s
    #     = mol^(1-n) * m^(3(n-1)) / s
    power_m = 3.0 * (overall_order - 1.0)
    power_mol = 1.0 - overall_order
    
    # Pint formatı
    return f"meter**({power_m}) * mole**({power_mol}) / second"

def calculate_rate_constant(k0, Ea, T, overall_order: float = 1.0, k0_units: str | None = None):
    """
    Arrhenius kinetiği: k = k0 * exp(-Ea/(R*T))
    """
    if T <= 0:
        raise ValueError("Sıcaklık (T) 0 Kelvin'den büyük olmalıdır.")

    if k0_units:
        k0_q = Q_(k0, k0_units)
    else:
        k0_q = Q_(k0, _k_units_for_order(overall_order))

    Ea_q = Q_(Ea, 'joule/mole')
    T_q = Q_(T, 'kelvin')
    R = Q_(8.314462618, 'joule/(mole*kelvin)')

    # Üstel terim boyutsuz olmalı
    exponent_term = (Ea_q/(R * T_q)).to_base_units()
    exponent = float(exponent_term.magnitude)
    
    k = k0_q * np.exp(-exponent)
    return k.to_base_units()

def calculate_reactor_volume(
    F_A0,
    C_A0,
    k,
    X,
    n,
    reactor_type,
    C_B0=None,
    m=0,
    a: float = 1.0,
    b: float = 1.0,
    phase: str = 'liquid',
    epsilon: float = 0.0
):
    """
    CSTR veya PFR hacmi hesaplama.
    """
    if not (0.0 < X < 1.0):
        raise ValueError("X (dönüşüm) 0 ile 1 arasında olmalıdır.")
    if X > 0.99:
        raise ValueError("Dönüşüm oranı çok yüksek (maks 0.99).")
        
    if F_A0 <= 0 or C_A0 <= 0 or n < 0 or (C_B0 is not None and C_B0 < 0):
        raise ValueError("Girdiler pozitif olmalıdır.")

    F_A0_q = Q_(F_A0, 'mole/second')
    C_A0_q = Q_(C_A0, 'mole/meter**3')
    C_B0_q = Q_(C_B0, 'mole/meter**3') if C_B0 is not None else None

    overall_order = n + (m if C_B0 is not None else 0)

    if hasattr(k, 'units'):
        k_q = k
    else:
        k_q = Q_(k, _k_units_for_order(overall_order))

    eps_rate = Q_(1e-30, 'mole/(meter**3*second)')

    def rate(x: float):
        # Konsantrasyonlar
        if phase == 'gas':
            denom = (1.0 + epsilon * x)
            if abs(denom) < 1e-9: denom = 1e-9 if denom >= 0 else -1e-9
            
            ca = C_A0_q * (1.0 - x) / denom
            if C_B0_q is not None:
                cb = (C_B0_q - (b/a) * C_A0_q * x) / denom
            else:
                cb = None
        else:  # liquid
            ca = C_A0_q * (1.0 - x)
            if C_B0_q is not None:
                cb_raw = C_B0_q - (b/a) * C_A0_q * x
                if cb_raw.magnitude < 0: cb_raw = Q_(0.0, cb_raw.units)
                cb = cb_raw
            else:
                cb = None

        r = k_q * (ca**n) * ((cb**m) if (cb is not None and m > 0) else 1)
        if hasattr(r, 'magnitude') and r.magnitude <= 0:
            r = eps_rate
        return r.to('mole/(meter**3*second)')

    if reactor_type == 'CSTR':
        r_exit = rate(X)
        if r_exit.magnitude <= 0:
            raise ValueError("Çıkış hız ifadesi sıfır veya negatif.")
        V = (F_A0_q * X) / r_exit
        return V.to('meter**3')

    elif reactor_type == 'PFR':
        def integrand(x):
            r_x = rate(x)
            # 1/r_A birimi: (mol/m^3 s)^-1 = m^3 s / mol
            inv = (Q_(1.0, 'dimensionless') / r_x).to('meter**3 * second / mole').magnitude
            return inv
        try:
            integral_val, _ = quad(integrand, 0.0, X, limit=500, epsabs=1e-9, epsrel=1e-7)
        except Exception as e:
             raise ValueError(f"İntegral hatası: {str(e)}")
             
        # integral_val birimi: m^3 * s / mol (integrand'dan gelir)
        # V = F_A0 * integral
        # [V] = (mol/s) * (m^3 s / mol) = m^3
        V = F_A0_q * Q_(integral_val, 'meter**3 * second / mole')
        return V.to('meter**3')

    else:
        raise ValueError("Reaktör tipi 'CSTR' veya 'PFR' olmalı.")

def calculate_batch_time(
    C_A0,
    k,
    X,
    n,
    C_B0=None,
    m=0,
    a: float = 1.0,
    b: float = 1.0,
    phase: str = 'liquid',
    epsilon: float = 0.0
):
    """
    Kesikli reaktörde dönüşüm için gereken süre [s].
    """
    if not (0.0 < X < 1.0):
        raise ValueError("X (dönüşüm) 0 ile 1 arasında olmalıdır.")
    
    C_A0_q = Q_(C_A0, 'mole/meter**3')
    C_B0_q = Q_(C_B0, 'mole/meter**3') if C_B0 is not None else None
    overall_order = n + (m if C_B0 is not None else 0)
    
    if hasattr(k, 'units'):
        k_q = k
    else:
        k_q = Q_(k, _k_units_for_order(overall_order))

    eps_rate = Q_(1e-30, 'mole/(meter**3*second)')

    def rate(x: float):
        # Batch için hacim değişimi varsa konsantrasyonlar değişir
        # V = V0(1+eps*X)
        # N_A = N_A0(1-X)
        # C_A = N_A/V = N_A0(1-X) / (V0(1+eps*X)) = C_A0(1-X)/(1+eps*X)
        # Formüller akışlı sistemle aynı (sabit hacim veya değişken hacim)
        
        if phase == 'gas': # Değişken hacim
            denom = (1.0 + epsilon * x)
            if abs(denom) < 1e-9: denom = 1e-9
            ca = C_A0_q * (1.0 - x) / denom
            if C_B0_q is not None:
                cb = (C_B0_q - (b/a) * C_A0_q * x) / denom
            else:
                cb = None
        else: # Sabit hacim
            ca = C_A0_q * (1.0 - x)
            if C_B0_q is not None:
                cb = C_B0_q - (b/a) * C_A0_q * x
                if cb.magnitude < 0: cb = Q_(0.0, cb.units)
            else:
                cb = None
                
        r = k_q * (ca**n) * ((cb**m) if (cb is not None and m > 0) else 1)
        if hasattr(r, 'magnitude') and r.magnitude <= 0:
            r = eps_rate
        return r.to('mole/(meter**3*second)')

    def integrand(x: float):
        r_x = rate(x)
        # Batch: t = C_A0 * integral(dX / r)
        val = (C_A0_q / r_x).to('second').magnitude
        return val

    try:
        integral_val, _ = quad(integrand, 0.0, X, limit=500, epsabs=1e-9, epsrel=1e-7)
    except Exception as e:
        raise ValueError(f"İntegral hatası: {str(e)}")
        
    return Q_(integral_val, 'second')

def generate_levenspiel_data(
    C_A0,
    k,
    X_final,
    n,
    C_B0=None,
    m=0,
    a: float = 1.0,
    b: float = 1.0,
    phase: str = 'liquid',
    epsilon: float = 0.0,
    n_points: int = 100
):
    """
    Levenspiel grafiği (1/-rA vs X) için veri üretir.
    """
    xs = np.linspace(0.0, X_final, n_points)
    data = []
    
    C_A0_q = Q_(C_A0, 'mole/meter**3')
    C_B0_q = Q_(C_B0, 'mole/meter**3') if C_B0 is not None else None
    overall_order = n + (m if C_B0 is not None else 0)
    
    if hasattr(k, 'units'):
        k_q = k
    else:
        k_q = Q_(k, _k_units_for_order(overall_order))
        
    eps_rate = 1e-9
    
    for x in xs:
        if phase == 'gas':
            denom = (1.0 + epsilon * x)
            if abs(denom) < 1e-9: denom = 1e-9
            ca = C_A0_q * (1.0 - x) / denom
            if C_B0_q is not None:
                cb = (C_B0_q - (b/a) * C_A0_q * x) / denom
            else:
                cb = None
        else:
            ca = C_A0_q * (1.0 - x)
            if C_B0_q is not None:
                cb = C_B0_q - (b/a) * C_A0_q * x
                if cb.magnitude < 0: cb = Q_(0.0, cb.units)
            else:
                cb = None
                
        r_val = k_q * (ca**n) * ((cb**m) if (cb is not None and m > 0) else 1)
        r_mag = r_val.to('mole/(meter**3*second)').magnitude
        
        if r_mag <= 0: r_mag = eps_rate
            
        inv_r = 1.0 / r_mag
        
        data.append({
            'X': x,
            'rate': r_mag,
            'inv_rate': inv_r,
            'CA': ca.to('mole/meter**3').magnitude
        })
        
    return pd.DataFrame(data)