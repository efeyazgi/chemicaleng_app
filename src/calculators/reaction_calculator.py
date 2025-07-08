import math
from scipy.integrate import quad
from pint import UnitRegistry

# Birim sistemi
ureg = UnitRegistry()
Q_ = ureg.Quantity


def calculate_rate_constant(k0, Ea, T):
    """
    Arrhenius kinetiği: k = k0 * exp(-Ea/(R*T))
    k0: [1/s], Ea: [J/mol], T: [K]
    Dönen: k [1/s]
    """
    k0_q = Q_(k0, '1/second')
    Ea_q = Q_(Ea, 'joule/mole')
    T_q = Q_(T, 'kelvin')
    R = Q_(8.314, 'joule/(mole*kelvin)')
    k = k0_q * math.exp(-Ea_q/(R * T_q))
    return k.to('1/second').magnitude


def calculate_reactor_volume(F_A0, C_A0, k, X, n, reactor_type, C_B0=None, m=0):
    """
    CSTR veya PFR hacmi hesaplama.
    F_A0: molar akış hızı [mol/s]
    C_A0: başlangıç konsantrasyon [mol/m³]
    k: hız sabiti [1/s]
    X: dönüşüm
    n: CA mertebesi
    C_B0: (isteğe bağlı) B bileşeninin başlangıç konsantrasyonu [mol/m³]
    m: CB mertebesi
    reactor_type: 'CSTR' veya 'PFR'
    Dönen: pint.Quantity (m³)
    """
    # Hız ifadesi
    def rate(x):
        ca = C_A0 * (1 - x)
        if C_B0 is None:
            return k * ca**n
        else:
            cb = C_B0 * (1 - x)
            return k * ca**n * cb**m

    if reactor_type == 'CSTR':
        r_exit = rate(X)
        V = (F_A0 * X) / r_exit
        return Q_(V, 'meter**3')

    elif reactor_type == 'PFR':
        integrand = lambda x: 1.0 / rate(x)
        integral_val, _ = quad(integrand, 0, X)
        V = F_A0 * integral_val
        return Q_(V, 'meter**3')

    else:
        raise ValueError("Reaktör tipi 'CSTR' veya 'PFR' olmalı.")


def calculate_batch_time(C_A0, k, X, n, C_B0=None, m=0):
    """
    Kesikli reaktörde dönüşüm için gereken süre [s].
    C_A0: başlangıç konsantrasyon [mol/m³]
    k: hız sabiti [1/s]
    X: dönüşüm
    n: CA mertebesi
    C_B0: (isteğe bağlı) B bileşen başlangıç konsantrasyonu [mol/m³]
    m: CB mertebesi
    Dönen: pint.Quantity (s)
    """
    def rate(x):
        ca = C_A0 * (1 - x)
        if C_B0 is None:
            return k * ca**n
        else:
            cb = C_B0 * (1 - x)
            return k * ca**n * cb**m

    integrand = lambda x: 1.0 / (rate(x) / C_A0)
    integral_val, _ = quad(integrand, 0, X)
    return Q_(integral_val, 'second')