import math
from scipy.integrate import quad
from pint import UnitRegistry
import numpy as np

# Birim sistemi
ureg = UnitRegistry()
Q_ = ureg.Quantity


def _k_units_for_order(overall_order: float) -> str:
    """Toplam mertebeye göre hız sabiti birimini döndürür.
    r = k * C^n_tot için [r] = mol/(m^3*s) olduğundan,
    [k] = (mol/m^3)^(1-n_tot) / s = m^(3(n_tot-1)) * mol^(1-n_tot) / s
    """
    if abs(overall_order - 1.0) < 1e-12:
        return '1/second'
    power_m = 3.0 * (overall_order - 1.0)
    power_mol = 1.0 - overall_order
    return f"meter**({power_m}) * mole**({power_mol}) / second"


def calculate_rate_constant(k0, Ea, T, overall_order: float = 1.0, k0_units: str | None = None):
    """
    Arrhenius kinetiği: k = k0 * exp(-Ea/(R*T))
    k0: sayısal değer (opsiyonel k0_units ile birlikte) veya beklenen birimde sayısal değer
    Ea: [J/mol], T: [K]
    overall_order: toplam mertebe (n + m)
    k0_units: verilirse k0 için açık birim. Verilmezse overall_order'dan türetilir.

    Dönen: pint.Quantity (temel birimlerde)
    """
    # k0 birimini belirle
    if k0_units:
        k0_q = Q_(k0, k0_units)
    else:
        k0_q = Q_(k0, _k_units_for_order(overall_order))

    Ea_q = Q_(Ea, 'joule/mole')
    T_q = Q_(T, 'kelvin')
    R = Q_(8.314462618, 'joule/(mole*kelvin)')

    exponent = float((Ea_q/(R * T_q)).to_base_units().magnitude)
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
    phase: str = 'liquid',  # 'liquid' veya 'gas'
    epsilon: float = 0.0
):
    """
    CSTR veya PFR hacmi hesaplama.
    F_A0: molar akış hızı [mol/s] (float)
    C_A0: başlangıç konsantrasyon [mol/m³] (float)
    k: hız sabiti (float veya pint.Quantity)
    X: dönüşüm (0-1)
    n: CA mertebesi
    reactor_type: 'CSTR' veya 'PFR'
    C_B0: (isteğe bağlı) B bileşeni başlangıç konsantrasyonu [mol/m³]
    m: CB mertebesi
    a, b: stokiyometrik katsayılar (a A + b B -> ...)
    phase: 'liquid' (sabit hacim) veya 'gas' (sabit T,P; epsilon düzeltmeli)
    epsilon: gaz fazı için hacim değişim parametresi (ε)

    Dönen: pint.Quantity (m³)
    """
    # Girdi kontrolü
    if not (0.0 < X < 1.0):
        raise ValueError("X (dönüşüm) 0 ile 1 arasında olmalıdır.")
    if F_A0 <= 0 or C_A0 <= 0 or n < 0 or (C_B0 is not None and C_B0 < 0):
        raise ValueError("Girdiler pozitif olmalıdır.")

    F_A0_q = Q_(F_A0, 'mole/second')
    C_A0_q = Q_(C_A0, 'mole/meter**3')
    C_B0_q = Q_(C_B0, 'mole/meter**3') if C_B0 is not None else None

    overall_order = n + (m if C_B0 is not None else 0)

    # k'yi Quantity'e dönüştür
    if hasattr(k, 'units'):
        k_q = k
    else:
        k_q = Q_(k, _k_units_for_order(overall_order))

    eps_rate = Q_(1e-30, 'mole/(meter**3*second)')

    def rate(x: float):
        # Konsantrasyonlar
        if phase == 'gas':
            denom = (1.0 + epsilon * x)
            ca = C_A0_q * (1.0 - x) / denom
            if C_B0_q is not None:
                cb_raw = C_B0_q - (b/a) * C_A0_q * x
                cb = cb_raw / denom
            else:
                cb = None
        else:  # liquid
            ca = C_A0_q * (1.0 - x)
            if C_B0_q is not None:
                cb_raw = C_B0_q - (b/a) * C_A0_q * x
                # Negatif olmaya eğilimliyse sıfıra sıkıştır
                if cb_raw.magnitude < 0:
                    cb_raw = Q_(0.0, cb_raw.units)
                cb = cb_raw
            else:
                cb = None

        r = k_q * (ca**n) * ((cb**m) if (cb is not None and m > 0) else 1)
        # Sayısal kararlılık
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
            inv = (Q_(1.0, 'dimensionless') / r_x).to('meter**3/mole').magnitude
            return inv
        integral_val, _ = quad(integrand, 0.0, X, limit=500, epsabs=1e-9, epsrel=1e-7)
        V = F_A0_q * integral_val
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
    C_A0: başlangıç konsantrasyon [mol/m³]
    k: hız sabiti (float veya pint.Quantity)
    X: dönüşüm (0-1)
    n: CA mertebesi
    C_B0: (isteğe bağlı) B bileşen başlangıç konsantrasyonu [mol/m³]
    m: CB mertebesi
    a, b: stokiyometri katsayıları
    phase: 'liquid' veya 'gas'
    epsilon: gaz fazı için hacim değişimi parametresi

    Dönen: pint.Quantity (s)
    """
    if not (0.0 < X < 1.0):
        raise ValueError("X (dönüşüm) 0 ile 1 arasında olmalıdır.")
    if C_A0 <= 0 or n < 0 or (C_B0 is not None and C_B0 < 0):
        raise ValueError("Girdiler pozitif olmalıdır.")

    C_A0_q = Q_(C_A0, 'mole/meter**3')
    C_B0_q = Q_(C_B0, 'mole/meter**3') if C_B0 is not None else None

    overall_order = n + (m if C_B0 is not None else 0)
    if hasattr(k, 'units'):
        k_q = k
    else:
        k_q = Q_(k, _k_units_for_order(overall_order))

    eps_rate = Q_(1e-30, 'mole/(meter**3*second)')

    def rate(x: float):
        if phase == 'gas':
            denom = (1.0 + epsilon * x)
            ca = C_A0_q * (1.0 - x) / denom
            if C_B0_q is not None:
                cb_raw = C_B0_q - (b/a) * C_A0_q * x
                cb = cb_raw / denom
            else:
                cb = None
        else:
            ca = C_A0_q * (1.0 - x)
            if C_B0_q is not None:
                cb_raw = C_B0_q - (b/a) * C_A0_q * x
                if cb_raw.magnitude < 0:
                    cb_raw = Q_(0.0, cb_raw.units)
                cb = cb_raw
            else:
                cb = None
        r = k_q * (ca**n) * ((cb**m) if (cb is not None and m > 0) else 1)
        if hasattr(r, 'magnitude') and r.magnitude <= 0:
            r = eps_rate
        return r.to('mole/(meter**3*second)')

    def integrand(x: float):
        r_x = rate(x)
        val = (C_A0_q / r_x).to('second').magnitude
        return val

    integral_val, _ = quad(integrand, 0.0, X, limit=500, epsabs=1e-9, epsrel=1e-7)
    return Q_(integral_val, 'second')