import pandas as pd
from pyfluids import HumidAir, InputHumidAir

def calculate_psychrometric_properties(T_db_C, P_Pa, rh_percent=None, T_wb_C=None):
    """
    Nemli havanın psikrometrik özelliklerini pyfluids kütüphanesi ile hesaplar.
    
    T_db_C: Kuru termometre sıcaklığı (°C)
    P_Pa: Basınç (Pa)
    rh_percent: Bağıl nem (%)
    T_wb_C: Yaş termometre sıcaklığı (°C)
    """
    inputs = [
        InputHumidAir.pressure(P_Pa),
        InputHumidAir.temperature(T_db_C)
    ]
    
    if rh_percent is not None:
        inputs.append(InputHumidAir.relative_humidity(rh_percent))
    elif T_wb_C is not None:
        inputs.append(InputHumidAir.wet_bulb_temperature(T_wb_C))
    else:
        raise ValueError("Hesaplama için Bağıl Nem veya Yaş Termometre Sıcaklığı sağlanmalıdır.")

    ha = HumidAir().with_state(*inputs)

    properties = {
        "Mutlak Nem (kg su/kg kuru hava)": ha.humidity,
        "Bağıl Nem (%)": ha.relative_humidity,
        "Entalpi (kJ/kg kuru hava)": ha.enthalpy / 1000,
        "Çiğ Noktası Sıcaklığı (°C)": ha.dew_temperature,
        "Yaş Termometre Sıcaklığı (°C)": ha.wet_bulb_temperature,
        "Özgül Hacim (m³/kg kuru hava)": ha.specific_volume,
    }
    
    df = pd.DataFrame(list(properties.items()), columns=['Özellik', 'Değer'])
    return df
