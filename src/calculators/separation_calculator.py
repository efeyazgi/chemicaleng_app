import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from scipy.interpolate import interp1d
from typing import Tuple, List

# Antoine coefficients for a small set of common chemicals.
# log10(P_mmHg) = A - B/(T + C) where T is in Celsius
# P_mmHg is converted to Pa with 1 mmHg = 133.322368 Pa
ANTOINE_COEFFS = {
    "water": (8.07131, 1730.63, 233.426),
    "ethanol": (8.20417, 1642.89, 230.3),
    "methanol": (8.07240, 1574.99, 238.0),
    "benzene": (6.89272, 1203.531, 219.888),
    "toluene": (6.95465, 1344.8, 219.48),
    "acetone": (7.02447, 1161.0, 224.0),
    "ammonia": (7.36059, 794.7, 227.0),
    "carbon dioxide": (6.81228, 1301.0, -3.494),
    "oxygen": (6.69149, 343.5, -6.0),
    "nitrogen": (6.49510, 352.0, -6.0),
    "air": (6.50000, 350.0, -6.0),
    "methane": (6.61184, 389.93, -6.0),
    "propane": (4.53678, 699.7, -29.1),
    "butane": (4.35576, 795.7, -6.0),
}

_MMHG_TO_PA = 133.322368


def _psat(T: float, A: float, B: float, C: float) -> float:
    """Calculate saturation pressure (Pa) using the Antoine equation."""
    return 10 ** (A - B / (T + C)) * _MMHG_TO_PA


def generate_vle_data(chem1: str, chem2: str, P: float, n_points: int = 50) -> pd.DataFrame:
    """Generate VLE data for an ideal binary system using Antoine equations."""
    if chem1 not in ANTOINE_COEFFS or chem2 not in ANTOINE_COEFFS:
        raise ValueError("Antoine coefficients for one of the chemicals are unavailable")

    A1, B1, C1 = ANTOINE_COEFFS[chem1]
    A2, B2, C2 = ANTOINE_COEFFS[chem2]

    def psat1(T: float) -> float:
        return _psat(T, A1, B1, C1)

    def psat2(T: float) -> float:
        return _psat(T, A2, B2, C2)

    xs = np.linspace(0.0, 1.0, n_points)
    data = []

    for x1 in xs:
        if x1 == 0:
            data.append({"x": 0.0, "y": 0.0})
            continue
        if x1 == 1:
            data.append({"x": 1.0, "y": 1.0})
            continue

        def equilibrium_temp(T: float) -> float:
            return x1 * psat1(T) + (1.0 - x1) * psat2(T) - P

        T_guess = 80.0
        T_solution = float(fsolve(equilibrium_temp, T_guess)[0])
        y1 = x1 * psat1(T_solution) / P
        data.append({"x": x1, "y": y1})

    df = pd.DataFrame(data)
    return df


def calculate_mccabe_thiele_lines(
    chem1: str,
    chem2: str,
    P: float,
    zF: float,
    xD: float,
    xB: float,
    q: float,
    R: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute equilibrium and operating lines for the McCabe-Thiele diagram."""
    vle_df = generate_vle_data(chem1, chem2, P)
    eq_curve = interp1d(vle_df["x"], vle_df["y"], kind="cubic", fill_value="extrapolate")

    if q == 1:
        q_line_x = [zF, zF]
        q_line_y = [zF, eq_curve(zF)]
        slope_q = None
        intercept_q = None
    else:
        slope_q = q / (q - 1.0)
        intercept_q = -zF / (q - 1.0)
        q_line_x = np.linspace(xB, xD, 20)
        q_line_y = slope_q * q_line_x + intercept_q

    q_line_df = pd.DataFrame({"x": q_line_x, "y": q_line_y})

    slope_rect = R / (R + 1.0)
    intercept_rect = xD / (R + 1.0)

    if slope_q is None:
        x_intersect = zF
        y_intersect = slope_rect * x_intersect + intercept_rect
    else:
        x_intersect = (intercept_rect - intercept_q) / (slope_q - slope_rect)
        y_intersect = slope_rect * x_intersect + intercept_rect

    rect_x = np.linspace(x_intersect, xD, 20)
    rect_y = slope_rect * rect_x + intercept_rect
    rect_line_df = pd.DataFrame({"x": rect_x, "y": rect_y})

    slope_strip = (y_intersect - xB) / (x_intersect - xB)
    intercept_strip = y_intersect - slope_strip * x_intersect
    strip_x = np.linspace(xB, x_intersect, 20)
    strip_y = slope_strip * strip_x + intercept_strip
    strip_line_df = pd.DataFrame({"x": strip_x, "y": strip_y})

    return vle_df, q_line_df, rect_line_df, strip_line_df


def calculate_theoretical_trays(
    chem1: str,
    chem2: str,
    P: float,
    zF: float,
    xD: float,
    xB: float,
    q: float,
    R: float,
) -> Tuple[int, List[Tuple[float, float]]]:
    """Estimate the number of theoretical trays using tray stepping."""
    vle_df, q_df, rect_df, strip_df = calculate_mccabe_thiele_lines(chem1, chem2, P, zF, xD, xB, q, R)

    eq = interp1d(vle_df["x"], vle_df["y"], kind="linear", fill_value="extrapolate")

    if q == 1:
        x_intersect = zF
    else:
        slope_q = q / (q - 1.0)
        intercept_q = -zF / (q - 1.0)
        slope_rect = R / (R + 1.0)
        intercept_rect = xD / (R + 1.0)
        x_intersect = (intercept_rect - intercept_q) / (slope_q - slope_rect)

    slope_rect = R / (R + 1.0)
    intercept_rect = xD / (R + 1.0)
    slope_strip = (slope_rect * x_intersect + intercept_rect - xB) / (x_intersect - xB)
    intercept_strip = slope_rect * x_intersect + intercept_rect - slope_strip * x_intersect

    x = xD
    y = xD
    points: List[Tuple[float, float]] = [(x, y)]
    trays = 0

    while x > xB:
        def horiz_func(xx: float) -> float:
            return eq(xx) - y

        x_new = float(fsolve(horiz_func, x)[0])
        x_new = max(min(x_new, 1.0), 0.0)
        points.append((x_new, y))

        if x_new >= x_intersect:
            y = slope_rect * x_new + intercept_rect
        else:
            y = slope_strip * x_new + intercept_strip
        points.append((x_new, y))

        trays += 1
        x = x_new
        if trays > 200:
            break
        if x <= xB:
            break

    return trays, points
