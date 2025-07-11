import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from typing import Tuple, List

# ---------------- McCabe–Thiele Separation Calculator ----------------
# Gerçek VLE, Raoult Yasası ve Antoine denklemi ile hesaplanır.

# Antoine katsayıları (T: °C, P_sat: mmHg)
ANTOINE_COEFFS = {
    'water':          {'A': 8.07131, 'B': 1730.63,  'C': 233.426},
    'ethanol':        {'A': 8.20417, 'B': 1642.89,  'C': 230.3},
    'methanol':       {'A': 8.07240, 'B': 1574.99,  'C': 238.0},
    'benzene':        {'A': 6.90565, 'B': 1211.033, 'C': 220.790},
    'toluene':        {'A': 6.95464, 'B': 1344.800, 'C': 219.480},
    'acetone':        {'A': 7.02447, 'B': 1161.0,   'C': 224.0},
    'ammonia':        {'A': 7.36059, 'B': 794.7,    'C': 227.0},
    'carbon dioxide': {'A': 6.81228, 'B': 1301.0,   'C': -3.494},
    'oxygen':         {'A': 6.69149, 'B': 343.5,    'C': -6.0},
    'nitrogen':       {'A': 6.49510, 'B': 352.0,    'C': -6.0},
    'air':            {'A': 6.50000, 'B': 350.0,    'C': -6.0},
    'methane':        {'A': 6.61184, 'B': 389.93,   'C': -6.0},
    'propane':        {'A': 4.53678, 'B': 699.7,    'C': -29.1},
    'butane':         {'A': 4.35576, 'B': 795.7,    'C': -6.0}
}

_MMHG_TO_PA = 133.322

def _psat_mmHg(T: float, A: float, B: float, C: float) -> float:
    """Antoine parametrelerinden mmHg cinsinden doyma basıncını hesaplar."""
    return 10 ** (A - (B / (T + C)))

def generate_vle_data(chem1: str, chem2: str, P: float, n_points: int = 50) -> pd.DataFrame:
    """Verilen kimyasallar ve basınç için Buhar-Sıvı Denge (VLE) verisi üretir."""
    if chem1 not in ANTOINE_COEFFS or chem2 not in ANTOINE_COEFFS:
        raise ValueError(f"Antoine katsayıları mevcut değil: {chem1}, {chem2}")
    
    A1, B1, C1 = ANTOINE_COEFFS[chem1].values()
    A2, B2, C2 = ANTOINE_COEFFS[chem2].values()

    def psat1(T): return _psat_mmHg(T, A1, B1, C1)
    def psat2(T): return _psat_mmHg(T, A2, B2, C2)

    P_mmHg = P / _MMHG_TO_PA
    xs = np.linspace(0.0, 1.0, n_points)
    data: List[Tuple[float, float]] = []

    for x1 in xs:
        if x1 == 0:
            def eq_temp_0(T): return psat2(T) - P_mmHg
            T_bub = float(fsolve(eq_temp_0, 100)[0])
            y1 = 0
        elif x1 == 1:
            def eq_temp_1(T): return psat1(T) - P_mmHg
            T_bub = float(fsolve(eq_temp_1, 80)[0])
            y1 = 1
        else:
            def eq_temp(T): return x1 * psat1(T) + (1 - x1) * psat2(T) - P_mmHg
            T_guess = (B1 / (A1 - np.log10(P_mmHg)) - C1 + B2 / (A2 - np.log10(P_mmHg)) - C2) / 2
            try:
                T_bub = float(fsolve(eq_temp, T_guess)[0])
                y1 = x1 * psat1(T_bub) / P_mmHg
            except:
                continue
        data.append((x1, y1))
            
    return pd.DataFrame(data, columns=['x', 'y']).sort_values('x').reset_index(drop=True)

def calculate_mccabe_thiele_lines(
    chem1: str, chem2: str, P: float, zF: float, xD: float, xB: float, q: float, R: float
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Grafik için gerekli tüm doğruları (VLE, q, zenginleştirme, soyma) hesaplar."""
    vle_df = generate_vle_data(chem1, chem2, P)
    
    m_r = R / (R + 1)
    b_r = xD / (R + 1)
    
    if q == 1.0:
        x_int = zF
        # q-doğrusunun denge eğrisini kestiği noktayı bul
        y_for_zF_on_vle = np.interp(zF, vle_df['x'], vle_df['y'])
        qx, qy = np.repeat(zF, 2), np.array([zF, y_for_zF_on_vle])
    else:
        m_q = q / (q - 1)
        b_q = -zF / (q - 1)
        x_int = (b_r - b_q) / (m_q - m_r)
        qx = np.linspace(xB, xD, 2)
        qy = m_q * qx + b_q

    y_int = m_r * x_int + b_r
    m_s = (y_int - xB) / (x_int - xB) if (x_int - xB) != 0 else np.inf
    
    q_df = pd.DataFrame({'x': qx, 'y': qy})
    rect_df = pd.DataFrame({'x': [x_int, xD], 'y': [y_int, xD]})
    strip_df = pd.DataFrame({'x': [xB, x_int], 'y': [xB, y_int]})
    
    return vle_df, q_df, rect_df, strip_df

def calculate_theoretical_trays(
    chem1: str, chem2: str, P: float, zF: float, xD: float, xB: float, q: float, R: float,
    max_trays: int = 50, tol: float = 1e-5
) -> Tuple[int, List[Tuple[float, float]]]:
    """Teorik raf sayısını ve grafik adımlarını hesaplar."""
    vle_df = generate_vle_data(chem1, chem2, P)
    
    # Raf sayma için fsolve yerine daha kararlı olan interpolasyon kullanılır.
    # Bu, bazı durumlarda fsolve'un çözüm bulamama sorununu önler.
    y_to_x_interp = interp1d(vle_df['y'], vle_df['x'], kind='linear', fill_value='extrapolate')

    m_r = R / (R + 1)
    b_r = xD / (R + 1)

    if q == 1.0:
        x_int = zF
    else:
        m_q = q / (q - 1)
        b_q = -zF / (q - 1)
        x_int = (b_r - b_q) / (m_q - m_r)
    y_int = m_r * x_int + b_r

    m_s = (y_int - xB) / (x_int - xB) if (x_int - xB) != 0 else np.inf
    b_s = y_int - m_s * x_int
    
    x, y = xD, xD
    steps: List[Tuple[float, float]] = [(x, y)]
    trays = 0
    
    for _ in range(max_trays):
        # Yatay adım (y sabit, denge eğrisine git)
        x_new = float(y_to_x_interp(y))
        steps.append((x_new, y))
        
        # Dikey adım (x_new sabit, ilgili işletme doğrusuna git)
        y_new = m_r * x_new + b_r if x_new >= x_int else m_s * x_new + b_s
        steps.append((x_new, y_new))
        
        trays += 1
        x, y = x_new, y_new
        
        if x <= xB + tol:
            break
            
    return trays, steps
