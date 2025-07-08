import numpy as np
import matplotlib.pyplot as plt
from pyfluids import HumidAir, InputHumidAir


def calculate_psychrometric_properties(T_db_C, P_Pa, rh_percent=None, T_wb_C=None):
    """
    Nemli havanın psikrometrik özelliklerini pyfluids ile hesaplar.

    Parametreler:
      T_db_C: kuru termometre sıcaklığı (°C)
      P_Pa: basınç (Pa)
      rh_percent: bağıl nem (%) [0-100]
      T_wb_C: yaş termometre sıcaklığı (°C)

    Dönen: sözlük {'Özellik': değer}
    """
    # Girdi hazırlığı
    inputs = [
        InputHumidAir.pressure(P_Pa),
        InputHumidAir.temperature(T_db_C)
    ]
    if rh_percent is not None:
        inputs.append(InputHumidAir.relative_humidity(rh_percent/100.0))
    elif T_wb_C is not None:
        inputs.append(InputHumidAir.wet_bulb_temperature(T_wb_C))
    else:
        raise ValueError("RH (%) veya yaş termometre sıcaklığı belirtilmeli.")

    ha = HumidAir().with_state(*inputs)

    props = {
        "T_db (°C)": T_db_C,
        "P (Pa)": P_Pa,
        "RH (%)": ha.relative_humidity * 100,
        "T_wb (°C)": ha.wet_bulb_temperature,
        "h (kJ/kg_dry)": ha.enthalpy / 1000,
        "w (kg_water/kg_dry)": ha.humidity,
        "v (m³/kg_dry)": ha.specific_volume,
        "T_dp (°C)": ha.dew_temperature,
    }
    return props


def generate_psychrometric_chart(P_Pa, T_min=0, T_max=50, RH_lines=None):
    """
    Psikrometrik diyagram oluşturur: doyma eğrisi ve iso-RH çizgileri.

    P_Pa: basınç (Pa)
    T_min, T_max: DBT aralığı (°C)
    RH_lines: çizilecek bağıl nem yüzdeleri listesi (örn. [10,30,50,70,90])

    Dönen: matplotlib.figure.Figure
    """
    if RH_lines is None:
        RH_lines = [10, 30, 50, 70, 90]

    # DBT ekseni
    Tdb = np.linspace(T_min, T_max, 101)
    # Doygun nem oranı (w) hesabı
    w_sat = []
    for T in Tdb:
        ha = HumidAir().with_state(
            InputHumidAir.pressure(P_Pa),
            InputHumidAir.temperature(T),
            InputHumidAir.relative_humidity(1.0)
        )
        w_sat.append(ha.humidity)
    w_sat = np.array(w_sat)

    fig, ax = plt.subplots(figsize=(8, 6))
    # Doygun eğri
    ax.plot(Tdb, w_sat, 'k-', label='RH 100% (Doygun)')
    # Iso-RH çizgileri
    for rh in RH_lines:
        ax.plot(Tdb, w_sat * (rh/100.0), '--', label=f'RH {rh}%')

    ax.set_xlabel('Kuru Termometre Sıcaklığı (°C)')
    ax.set_ylabel('Nem Oranı w (kg su/kg kuru hava)')
    ax.set_title('Psikrometrik Diyagram')
    ax.legend(loc='best', fontsize='small')
    ax.grid(True)

    return fig