import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from typing import Tuple, List

# ---------------- McCabe–Thiele Separation Calculator ----------------
# Real VLE via Raoult's Law + Antoine equation for multiple chemicals

# Antoine coefficients (T in °C, P_sat in mmHg)
ANTOINE_COEFFS = {
    'water':           {'A': 8.07131, 'B': 1730.63,  'C': 233.426},
    'ethanol':         {'A': 8.20417, 'B': 1642.89,  'C': 230.3},
    'methanol':        {'A': 8.07240, 'B': 1574.99,  'C': 238.0},
    'benzene':         {'A': 6.90565, 'B': 1211.033, 'C': 220.790},
    'toluene':         {'A': 6.95464, 'B': 1344.800, 'C': 219.480},
    'acetone':         {'A': 7.02447, 'B': 1161.0,   'C': 224.0},
    'ammonia':         {'A': 7.36059, 'B': 794.7,    'C': 227.0},
    'carbon dioxide':  {'A': 6.81228, 'B': 1301.0,   'C': -3.494},
    'oxygen':          {'A': 6.69149, 'B': 343.5,    'C': -6.0},
    'nitrogen':        {'A': 6.49510, 'B': 352.0,    'C': -6.0},
    'air':             {'A': 6.50000, 'B': 350.0,    'C': -6.0},
    'methane':         {'A': 6.61184, 'B': 389.93,   'C': -6.0},
    'propane':         {'A': 4.53678, 'B': 699.7,    'C': -29.1},
    'butane':          {'A': 4.35576, 'B': 795.7,    'C': -6.0}
}

_MMHG_TO_PA = 133.322

def _psat_mmHg(T: float, A: float, B: float, C: float) -> float:
    """Compute saturation pressure in Pa from Antoine parameters."""
    return 10 ** (A - (B / (T + C))) * _MMHG_TO_PA


def generate_vle_data(chem1: str, chem2: str, P: float, n_points: int = 50) -> pd.DataFrame:
    if chem1 not in ANTOINE_COEFFS or chem2 not in ANTOINE_COEFFS:
        raise ValueError(f"Antoine coefficients unavailable for: {chem1}, {chem2}")
    A1, B1, C1 = ANTOINE_COEFFS[chem1].values()
    A2, B2, C2 = ANTOINE_COEFFS[chem2].values()
    def psat1(T): return _psat_mmHg(T, A1, B1, C1)
    def psat2(T): return _psat_mmHg(T, A2, B2, C2)
    P_mmHg = P / _MMHG_TO_PA
    xs = np.linspace(0.01, 0.99, n_points)
    data: List[Tuple[float, float]] = []
    for x1 in xs:
        def eq_temp(T): return x1 * psat1(T) / P_mmHg + (1 - x1) * psat2(T) / P_mmHg - 1
        T_guess = (B1 / (A1 - np.log10(P_mmHg)) - C1 + B2 / (A2 - np.log10(P_mmHg)) - C2) / 2
        try:
            T_bub = float(fsolve(eq_temp, T_guess)[0])
            y1 = x1 * psat1(T_bub) / P_mmHg
            data.append((x1, y1))
        except:
            continue
    return pd.DataFrame(data, columns=['x', 'y']).sort_values('x').reset_index(drop=True)


def calculate_mccabe_thiele_lines(
    chem1: str,
    chem2: str,
    P: float,
    zF: float,
    xD: float,
    xB: float,
    q: float,
    R: float
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    vle_df = generate_vle_data(chem1, chem2, P)
    eq_interp = interp1d(vle_df['x'], vle_df['y'], kind='cubic', fill_value='extrapolate')
    if q == 1.0:
        qx, qy = np.repeat(zF, 2), np.array([0.0, 1.0])
    else:
        m_q, b_q = q/(q-1), -zF/(q-1)
        qx = np.linspace(xB, xD, 100); qy = m_q*qx + b_q
    q_df = pd.DataFrame({'x': qx, 'y': qy})
    m_r, b_r = R/(R+1), xD/(R+1)
    if q == 1.0:
        x_int = zF
    else:
        x_int = (b_r - b_q) / (m_q - m_r)
    y_int = m_r * x_int + b_r
    rx = np.linspace(x_int, xD, 100); ry = m_r * rx + b_r
    rect_df = pd.DataFrame({'x': rx, 'y': ry})
    m_s, b_s = (y_int - xB)/(x_int - xB), y_int - (y_int - xB)/(x_int - xB)*x_int
    sx = np.linspace(xB, x_int, 100); sy = m_s * sx + b_s
    strip_df = pd.DataFrame({'x': sx, 'y': sy})
    return vle_df, q_df, rect_df, strip_df


def calculate_theoretical_trays(
    chem1: str,
    chem2: str,
    P: float,
    zF: float,
    xD: float,
    xB: float,
    q: float,
    R: float,
    max_trays: int = 200,
    tol: float = 1e-5
) -> Tuple[int, List[Tuple[float, float]]]:
    vle_df, q_df, rect_df, strip_df = calculate_mccabe_thiele_lines(
        chem1, chem2, P, zF, xD, xB, q, R
    )
    eq_interp = interp1d(vle_df['x'], vle_df['y'], kind='linear', fill_value='extrapolate')
    if q == 1.0:
        x_int = zF
    else:
        m_q, b_q = q/(q-1), -zF/(q-1)
        m_r, b_r = R/(R+1), xD/(R+1)
        x_int = (b_r - b_q)/(m_q - m_r)
    m_r, b_r = R/(R+1), xD/(R+1)
    m_s = (strip_df['y'].iloc[-1] - xB)/(x_int - xB)
    b_s = strip_df['y'].iloc[-1] - m_s * x_int
    x, y = xD, xD
    steps: List[Tuple[float, float]] = [(x, y)]
    trays = 0
    for _ in range(max_trays):
        x_new = float(fsolve(lambda xx: eq_interp(xx) - y, x)[0])
        x_new = np.clip(x_new, 0.0, 1.0)
        steps.append((x_new, y))
        y = m_r * x_new + b_r if x_new >= x_int else m_s * x_new + b_s
        steps.append((x_new, y))
        trays += 1
        x = x_new
        if x <= xB + tol:
            break
    return trays, steps
