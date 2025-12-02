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

    Dönen: sözlük {'Özellik': değer} veya hata mesajı içeren sözlük
    """
    # Girdi kontrolü
    if P_Pa <= 0:
        return {"Hata": "Basınç sıfırdan büyük olmalıdır."}
    
    inputs = [
        InputHumidAir.pressure(P_Pa),
        InputHumidAir.temperature(T_db_C)
    ]
    
    if rh_percent is not None:
        if not (0 <= rh_percent <= 100):
             return {"Hata": "Bağıl nem %0 ile %100 arasında olmalıdır."}
        # PyFluids (CoolProp) RH'yi yüzde (0-100) olarak bekler
        inputs.append(InputHumidAir.relative_humidity(rh_percent))
    elif T_wb_C is not None:
        # Tolerans kontrolü: T_wb, T_db'den çok az büyükse (ölçüm hatası vs.), eşit kabul et.
        if T_wb_C > T_db_C:
            if (T_wb_C - T_db_C) < 0.1: # 0.1 derece tolerans
                T_wb_C = T_db_C
            else:
                return {"Hata": "Yaş termometre sıcaklığı, kuru termometre sıcaklığından büyük olamaz."}
        inputs.append(InputHumidAir.wet_bulb_temperature(T_wb_C))
    else:
        return {"Hata": "RH (%) veya yaş termometre sıcaklığı belirtilmeli."}

    try:
        ha = HumidAir().with_state(*inputs)
        
        props = {
            "T_db (°C)": T_db_C,
            "P (Pa)": P_Pa,
            "RH (%)": ha.relative_humidity, # Zaten yüzde olarak dönüyor
            "T_wb (°C)": ha.wet_bulb_temperature,
            "h (kJ/kg_dry)": ha.enthalpy / 1000,
            "w (kg_water/kg_dry)": ha.humidity,
            "v (m³/kg_dry)": ha.specific_volume,
            "T_dp (°C)": ha.dew_temperature,
        }
        return props
    except Exception as e:
        return {"Hata": f"Hesaplama hatası: {str(e)}"}


def generate_psychrometric_chart(P_Pa, T_min=0, T_max=50, RH_lines=None):
    """
    Psikrometrik diyagram oluşturur: doyma eğrisi ve iso-RH çizgileri.

    P_Pa: basınç (Pa)
    T_min, T_max: DBT aralığı (°C)
    RH_lines: çizilecek bağıl nem yüzdeleri listesi (örn. [10,30,50,70,90])

    Dönen: matplotlib.figure.Figure
    """
    if P_Pa <= 0:
        raise ValueError("Basınç sıfırdan büyük olmalıdır.")
    if T_min >= T_max:
        raise ValueError("T_min, T_max'tan küçük olmalıdır.")

    if RH_lines is None:
        RH_lines = [10, 30, 50, 70, 90]

    # DBT ekseni
    Tdb = np.linspace(T_min, T_max, 50) # Performans için nokta sayısını 50'ye düşürdük
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Her bir RH çizgisi için w değerlerini hesapla
    # RH=100 (Doygunluk) dahil
    all_lines = sorted(list(set(RH_lines + [100])))
    
    for rh in all_lines:
        w_vals = []
        valid_T = []
        for T in Tdb:
            try:
                ha = HumidAir().with_state(
                    InputHumidAir.pressure(P_Pa),
                    InputHumidAir.temperature(T),
                    InputHumidAir.relative_humidity(rh) # Yüzde olarak gönderilmeli
                )
                w_vals.append(ha.humidity)
                valid_T.append(T)
            except:
                # Hesaplama hatası olursa (örn. aşırı sıcaklık/basınç) bu noktayı atla
                continue
        
        if not valid_T:
            continue
            
        style = 'k-' if rh == 100 else '--'
        label = f'RH {rh}%' + (' (Doygun)' if rh == 100 else '')
        ax.plot(valid_T, w_vals, style, label=label)

    ax.set_xlabel('Kuru Termometre Sıcaklığı (°C)')
    ax.set_ylabel('Nem Oranı w (kg su/kg kuru hava)')
    ax.set_title(f'Psikrometrik Diyagram (P = {P_Pa/1000:.1f} kPa)')
    ax.legend(loc='best', fontsize='small')
    ax.grid(True, alpha=0.3)

    return fig