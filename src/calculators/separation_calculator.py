import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from thermo import Chemical, ChemicalConstantsPackage, PropertyCorrelationsPackage, CEOSLiquid, CEOSGas, FlashVL
from thermo.eos_mix import PRMIX

def get_vle_data_for_separation(chem1, chem2, P):
    """
    Sadece Ayırma İşlemleri modülü için ham VLE verisi (x, y) döndürür.
    """
    constants, correlations = ChemicalConstantsPackage.from_IDs([chem1, chem2])
    eos_kwargs = dict(Tcs=constants.Tcs, Pcs=constants.Pcs, omegas=constants.omegas)
    liquid = CEOSLiquid(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
    gas = CEOSGas(PRMIX, HeatCapacityGases=correlations.HeatCapacityGases, eos_kwargs=eos_kwargs)
    flash = FlashVL(constants=constants, correlations=correlations, liquid=liquid, gas=gas)

    results = []
    compositions = np.linspace(0.001, 0.999, 25)
    
    t_guess_error = None
    try:
        # Kaynama noktalarını alırken hata oluşursa yakala
        t_chem1 = Chemical(chem1, P=P).Tb
        t_chem2 = Chemical(chem2, P=P).Tb
        if t_chem1 is None or t_chem2 is None:
            raise ValueError("Bileşenlerden biri için kaynama noktası hesaplanamadı.")
        t_guess = (t_chem1 + t_chem2) / 2.0
    except Exception as e:
        t_guess = 350.0 # Genel bir başlangıç değeri
        t_guess_error = str(e)

    for z1 in compositions:
        try:
            # T_guess parametresi bu thermo versiyonunda desteklenmiyor.
            # Kütüphanenin kendi başlangıç tahminini kullanmasına izin ver.
            res = flash.flash(P=P, zs=[z1, 1-z1])
            if res.phase == 'L/V':
                results.append({'x': res.xs[0], 'y': res.ys[0]})
        except Exception as e:
            # Hatanın nedenini görmek için terminale yazdır
            print(f"Debug: Flash calculation failed for z1={z1:.3f}. Error: {e}")
            continue
            
    if not results:
        error_message = (
            f"Bu basınçta ({P} Pa) denge verisi oluşturulamadı. "
            "Olası Nedenler:\n"
            "1. Basınç, seçilen bileşenlerin kritik basıncının üzerinde veya çok düşük olabilir.\n"
            "2. Başlangıç sıcaklığı tahmini başarısız oldu. "
        )
        if t_guess_error:
            error_message += f"(Detay: {t_guess_error})"
        raise ValueError(error_message)
         
    df = pd.DataFrame(results)
    df = df.sort_values(by='x').reset_index(drop=True)
    return df

def calculate_mccabe_thiele_lines(chem1, chem2, P, zF, xD, xB, q, R):
    """
    McCabe-Thiele analizi için gerekli tüm çizgilerin verilerini hesaplar.
    """
    # 1. Denge Eğrisi
    vle_df = get_vle_data_for_separation(chem1, chem2, P)
    # Denge eğrisini daha sonra kullanmak için bir interpolasyon fonksiyonu oluştur
    eq_curve = interp1d(vle_df['x'], vle_df['y'], kind='cubic', fill_value="extrapolate")

    # 2. q-Doğrusu
    if q == 1: # Doymuş sıvı
        q_line_x = [zF, zF]
        q_line_y = [zF, eq_curve(zF)]
    else:
        slope_q = q / (q - 1)
        intercept_q = -zF / (q - 1)
        q_line_x = np.linspace(xB, xD, 10)
        q_line_y = slope_q * q_line_x + intercept_q
    
    q_line_df = pd.DataFrame({'x': q_line_x, 'y': q_line_y})

    # 3. Zenginleştirme (Rectifying) İşletme Doğrusu
    slope_rect = R / (R + 1)
    intercept_rect = xD / (R + 1)
    
    # 4. Sıyırma (Stripping) İşletme Doğrusu ve Kesişim Noktası
    x_intersect = (intercept_rect - intercept_q) / (slope_q - slope_rect) if (slope_q - slope_rect) != 0 else zF
    y_intersect = slope_rect * x_intersect + intercept_rect
    
    # Zenginleştirme doğrusu verisi (xD'den kesişime kadar)
    rect_line_x = np.linspace(x_intersect, xD, 10)
    rect_line_y = slope_rect * rect_line_x + intercept_rect
    rect_line_df = pd.DataFrame({'x': rect_line_x, 'y': rect_line_y})
    
    # Sıyırma doğrusu verisi (xB'den kesişime kadar)
    strip_line_x = np.linspace(xB, x_intersect, 10)
    slope_strip = (y_intersect - xB) / (x_intersect - xB) if (x_intersect - xB) != 0 else 0
    intercept_strip = y_intersect - slope_strip * x_intersect
    strip_line_y = slope_strip * strip_line_x + intercept_strip
    strip_line_df = pd.DataFrame({'x': strip_line_x, 'y': strip_line_y})

    return vle_df, q_line_df, rect_line_df, strip_line_df
