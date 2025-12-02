import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from thermo import Chemical
from typing import Tuple, List, Dict

# ---------------- Helper Functions ----------------

def get_phase_enthalpy(chem_name: str, T: float, phase: str) -> float:
    """
    Belirli bir faz (sıvı veya buhar) için entalpiyi hesaplar (J/mol).
    Fazı zorlamak için basıncı manipüle ederiz.
    """
    # Kritik sıcaklık kontrolü yapılabilir ama basitlik için:
    # Sıvı için yüksek basınç, Buhar için düşük basınç varsayalım.
    # Ancak ideal olarak P sistem basıncı olmalı.
    # Eğer T, kaynama noktasının çok altındaysa buhar, çok üstündeyse sıvı hipotetiktir.
    
    try:
        c = Chemical(chem_name, T=T)
        Psat = c.Psat if c.Psat else 101325.0
        
        if phase == 'l':
            # Sıvı entalpisi için basıncı Psat'ın biraz üzerinde tutalım veya sistem basıncı
            # Basit yaklaşım: Doygun sıvı entalpisi
            # thermo kütüphanesinde fazı zorlamak bazen tricky olabilir.
            # P = Psat + epsilon -> Liquid
            c_l = Chemical(chem_name, T=T, P=Psat*1.01 if Psat else 101325)
            return c_l.H
        elif phase == 'v':
            # Buhar entalpisi
            # P = Psat - epsilon -> Vapor
            c_v = Chemical(chem_name, T=T, P=Psat*0.99 if Psat else 1000)
            return c_v.H
    except:
        return 0.0
    return 0.0

def get_mixture_enthalpy(chem1: str, chem2: str, x1: float, T: float, P: float, phase: str = None) -> float:
    """
    Karışımın entalpisini hesaplar (J/mol).
    İdeal karışım varsayımı: H_mix = x1*H1 + x2*H2
    """
    try:
        # Faz belirtilmediyse T ve P'ye göre otomatik belirlenir (Chemical varsayılanı)
        # Ancak biz VLE eğrileri için fazı zorlamak isteyebiliriz.
        
        h1 = get_phase_enthalpy(chem1, T, phase)
        h2 = get_phase_enthalpy(chem2, T, phase)
        
        return x1 * h1 + (1 - x1) * h2
    except:
        return 0.0

def calculate_q_from_T(chem1: str, chem2: str, P: float, zF: float, T_feed: float) -> float:
    """
    Besleme sıcaklığından q değerini hesaplar.
    q = (H_vapor_sat - H_feed) / (H_vapor_sat - H_liquid_sat)
    """
    # 1. Besleme kompozisyonunda (zF) kabarcık ve çiy noktası sıcaklıklarını bul
    # Basitlik için VLE fonksiyonunu kullanabiliriz veya tek nokta hesabı yapabiliriz.
    # Şimdilik VLE fonksiyonunu çağırıp interpolasyon yapalım (biraz yavaş olabilir ama güvenli)
    
    df = calculate_vle_thermo(chem1, chem2, P, n_points=11)
    
    # zF noktasındaki doygun sıvı ve buhar entalpileri
    # DİKKAT: Ponchon diyagramında aynı x (veya y) apsisindeki dikey farka bakıyoruz.
    # Yani zF kompozisyonundaki doymuş sıvı ve doymuş buhar.
    
    f_HL = interp1d(df['x'], df['HL'], kind='linear', fill_value='extrapolate')
    f_HV = interp1d(df['y'], df['HV'], kind='linear', fill_value='extrapolate') # y'ye bağlı HV
    
    HL_sat = float(f_HL(zF))
    HV_sat = float(f_HV(zF)) # zF buhar fazındayken entalpi
    
    # Besleme Entalpisi
    # H_feed. Eğer T_feed verilmişse:
    # Fazı tahmin etmemiz lazım.
    # T_bubble ve T_dew bulmamız lazım zF için.
    f_T_bub = interp1d(df['x'], df['T'], kind='linear', fill_value='extrapolate')
    f_T_dew = interp1d(df['y'], df['T'], kind='linear', fill_value='extrapolate')
    
    T_bub = float(f_T_bub(zF))
    T_dew = float(f_T_dew(zF))
    
    if T_feed <= T_bub:
        # Alt soğutulmuş sıvı veya doymuş sıvı
        phase = 'l'
    elif T_feed >= T_dew:
        # Kızgın buhar veya doymuş buhar
        phase = 'v'
    else:
        # İki fazlı bölge (Flash hesabı gerekir, zor)
        # Yaklaşık olarak T ile orantılı q?
        # q = (T_dew - T_feed) / (T_dew - T_bub) ? Bu sadece T-x-y diyagramında geçerli.
        # Entalpi üzerinden gidelim.
        # İki fazlı bölgede H_feed'i T ile bulmak için flash lazım.
        # Basitlik adına: T_feed verildiğinde tek faz varsayıyoruz veya q hesabı T üzerinden yapılıyor.
        phase = 'l' # Varsayılan
        
    H_feed = get_mixture_enthalpy(chem1, chem2, zF, T_feed, P, phase)
    
    # q formülü: (HV - HF) / (HV - HL)
    if abs(HV_sat - HL_sat) < 1e-5: return 1.0
    q = (HV_sat - H_feed) / (HV_sat - HL_sat)
    return q

def calculate_vle_thermo(chem1: str, chem2: str, P: float, n_points: int = 20) -> pd.DataFrame:
    if P <= 0:
        raise ValueError("Basınç sıfırdan büyük olmalıdır.")

    xs = np.linspace(0.0, 1.0, n_points)
    data = []

    # Saf maddelerin kaynama noktalarını bul (Sıcaklık tahmini için)
    try:
        Tb1 = Chemical(chem1, P=P).Tb
        Tb2 = Chemical(chem2, P=P).Tb
    except:
        Tb1, Tb2 = 373.15, 351.15 # Fallback

    for x1 in xs:
        x2 = 1.0 - x1
        
        # T_bub (Kabarcık noktası sıcaklığı) bulma
        # P = x1*P1sat(T) + x2*P2sat(T) denklemini çözen T
        def error_func(T):
            try:
                p1 = Chemical(chem1, T=T).Psat
                p2 = Chemical(chem2, T=T).Psat
                if p1 is None or p2 is None: return 1e5
                return x1 * p1 + x2 * p2 - P
            except:
                return 1e5
        
        # Başlangıç tahmini: Ağırlıklı ortalama
        T_guess = x1 * Tb1 + x2 * Tb2
        try:
            T_sol = fsolve(error_func, T_guess)[0]
        except:
            continue

        # y1 hesapla
        try:
            P1sat = Chemical(chem1, T=T_sol).Psat
            y1 = x1 * P1sat / P
            y1 = max(0.0, min(1.0, y1)) # Sınırla
        except:
            continue
            
        # Entalpileri Hesapla (J/mol)
        # H_L = x1*H_L1 + x2*H_L2
        # H_V = y1*H_V1 + y2*H_V2
        # Not: Karışım ısısını ihmal ediyoruz (İdeal karışım varsayımı)
        
        H_L1 = get_phase_enthalpy(chem1, T_sol, 'l')
        H_L2 = get_phase_enthalpy(chem2, T_sol, 'l')
        H_V1 = get_phase_enthalpy(chem1, T_sol, 'v')
        H_V2 = get_phase_enthalpy(chem2, T_sol, 'v')
        
        HL = x1 * H_L1 + x2 * H_L2
        HV = y1 * H_V1 + (1 - y1) * H_V2
        
        data.append({
            'x': x1, 
            'y': y1, 
            'T': T_sol, 
            'HL': HL, 
            'HV': HV
        })

    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=['x', 'y', 'T', 'HL', 'HV'])
        
    return df.sort_values('x').reset_index(drop=True)


# ---------------- McCabe-Thiele Method ----------------

def calculate_mccabe_thiele(
    chem1: str, chem2: str, P: float, zF: float, xD: float, xB: float, q: float, R: float
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, int, List[Tuple[float, float]]]:
    
    # 1. VLE Verisi
    vle_df = calculate_vle_thermo(chem1, chem2, P)
    if vle_df.empty:
        raise ValueError("VLE verisi oluşturulamadı.")

    # 2. İşletme Doğruları
    m_r = R / (R + 1)
    b_r = xD / (R + 1)
    
    # q-doğrusu ve kesişim
    if abs(q - 1.0) < 1e-9: # Doygun sıvı besleme
        x_int = zF
        # q-line dikey
        qx = np.array([zF, zF])
        # y değerini denge eğrisinden bulalım
        y_eq_at_zF = np.interp(zF, vle_df['x'], vle_df['y'])
        qy = np.array([zF, y_eq_at_zF])
    else:
        m_q = q / (q - 1)
        b_q = -zF / (q - 1)
        
        denom = (m_q - m_r)
        if abs(denom) < 1e-9: x_int = zF 
        else: x_int = (b_r - b_q) / denom
        
        # q-line çizimi için noktalar
        # zF'den kesişime kadar
        qx = np.linspace(min(zF, x_int), max(zF, x_int), 10)
        qy = m_q * qx + b_q

    y_int = m_r * x_int + b_r
    
    # Soyma doğrusu
    denom_s = (x_int - xB)
    if abs(denom_s) < 1e-9: m_s = 0
    else: m_s = (y_int - xB) / denom_s
    b_s = y_int - m_s * x_int
    
    # DataFrame'ler (Grafik için)
    rect_df = pd.DataFrame({'x': [x_int, xD], 'y': [y_int, xD]})
    strip_df = pd.DataFrame({'x': [xB, x_int], 'y': [xB, y_int]})
    q_df = pd.DataFrame({'x': qx, 'y': qy})
    
    # 3. Raf Sayımı (Stepping)
    steps = []
    x_curr, y_curr = xD, xD
    steps.append((x_curr, y_curr))
    
    trays = 0
    max_trays = 100
    
    # İnterpolasyon fonksiyonu
    eq_interp = interp1d(vle_df['y'], vle_df['x'], kind='linear', fill_value='extrapolate') # y -> x (ters)
    
    while x_curr > xB and trays < max_trays:
        # 1. Dengeye git (Yatay: y sabit, x değişir)
        # y_curr değerine karşılık gelen x dengesi
        try:
            x_eq = float(eq_interp(y_curr))
        except:
            break
            
        steps.append((x_eq, y_curr))
        x_curr = x_eq
        trays += 1
        
        if x_curr <= xB:
            break
            
        # 2. İşletme doğrusuna git (Dikey: x sabit, y değişir)
        if x_curr >= x_int:
            y_op = m_r * x_curr + b_r
        else:
            y_op = m_s * x_curr + b_s
            
        steps.append((x_curr, y_op))
        y_curr = y_op
        
    return vle_df, q_df, rect_df, strip_df, trays, steps


# ---------------- Ponchon-Savarit Method ----------------

def calculate_ponchon_savarit(
    chem1: str, chem2: str, P: float, zF: float, xD: float, xB: float, q: float, R: float
) -> Tuple[pd.DataFrame, Dict, int, List[Tuple[float, float]]]:
    
    # 1. VLE ve Entalpi Verisi
    df = calculate_vle_thermo(chem1, chem2, P)
    if df.empty:
        raise ValueError("Veri oluşturulamadı.")
        
    # İnterpolasyonlar
    # x -> HL, y -> HV, y -> x (denge), x -> y (denge)
    # Denge verileri (x-y)
    f_y_vs_x = interp1d(df['x'], df['y'], kind='linear', fill_value='extrapolate')
    f_x_vs_y = interp1d(df['y'], df['x'], kind='linear', fill_value='extrapolate')
    
    # Entalpi verileri
    f_HL_vs_x = interp1d(df['x'], df['HL'], kind='linear', fill_value='extrapolate')
    f_HV_vs_y = interp1d(df['y'], df['HV'], kind='linear', fill_value='extrapolate') # Dikkat: HV y'ye bağlı
    
    # 2. Delta Noktalarının Belirlenmesi
    
    # Besleme Noktası (F)
    # q = (HV_F - HF) / (HV_F - HL_F)  => HF entalpisi
    # Genelde q verilir.
    # HF = HV_F - q * (HV_F - HL_F)
    # Besleme buharı ve sıvısı doygun sıcaklıkta varsayılırsa:
    HL_F_sat = float(f_HL_vs_x(zF))
    HV_F_sat = float(f_HV_vs_y(zF)) # zF kompozisyonundaki buharın entalpisi (Dew point)
    # Ancak q tanımı genelde besleme koşulundaki entalpi üzerindendir.
    # HF = HL_F_sat * q + HV_F_sat * (1-q) ??? Hayır q = sıvı oranı.
    # q = (Isı to vaporize 1 mol feed) / (Molar latent heat)
    # q = (H_V - H_F) / (H_V - H_L)
    # H_F = H_V - q * (H_V - H_L)
    # Burada H_V ve H_L besleme kompozisyonundaki (zF) doygun buhar ve sıvı entalpileridir.
    # Not: f_HV_vs_y fonksiyonu y'ye göre HV verir. Besleme buhar fazındaysa y=zF olur.
    
    # Besleme entalpisi
    # Doygun sıvı ve buhar entalpilerini zF noktasında bulalım
    # DİKKAT: f_HV_vs_y fonksiyonu y girdisi alır.
    # Doygun buhar eğrisi üzerinde x=zF olan nokta değil, y=zF olan nokta entalpisi mi?
    # Ponchon diyagramında x ve y ekseni aynıdır (mol kesri).
    # Doygun sıvı eğrisi: (x, HL(x))
    # Doygun buhar eğrisi: (y, HV(y))
    
    H_sat_liq_F = float(f_HL_vs_x(zF))
    H_sat_vap_F = float(f_HV_vs_y(zF))
    
    HF = H_sat_vap_F * (1 - q) + H_sat_liq_F * q # Yaklaşık q tanımı
    
    # Distilat (D) ve Delta_D
    # Tam yoğuşturucu varsayımı: xD kompozisyonunda doymuş sıvı ürün.
    # (Reflux da doymuş sıvı)
    hD = float(f_HL_vs_x(xD)) # Ürün entalpisi
    # Delta_D koordinatları: (xD, Q_prime_D)
    # R = (Q_prime_D - HV_1) / (HV_1 - hD) ???
    # Daha basit: R = L/D.
    # Delta_D entalpisi (Q'_D) = hD + Qc/D
    # Qc/D = R * lambda ?
    # Enerji dengesi: V1 * HV1 = L0 * hD + D * hD + Qc
    # V1 = L0 + D = (R+1)D
    # (R+1)D * HV1 = (R+1)D * hD + Qc  => Qc = (R+1)D * (HV1 - hD)
    # Q'_D = hD + Qc/D = hD + (R+1)(HV1 - hD)
    # HV1: xD kompozisyonundaki dengedeki buharın entalpisi.
    # Tam yoğuşturucu ise y1 = xD.
    HV1 = float(f_HV_vs_y(xD))
    
    Q_prime_D = hD + (R + 1) * (HV1 - hD)
    
    # Dip Ürün (B) ve Delta_B
    # Delta_B koordinatları: (xB, Q_prime_B)
    # Toplam kütle ve enerji denkliğinden Delta_D, F ve Delta_B doğrusaldır.
    # F noktası: (zF, HF)
    # Delta_D: (xD, Q_prime_D)
    # Delta_B bu doğru üzerindedir ve x=xB'dedir.
    
    # Doğru denklemi (Delta_D - F):
    # Eğim m = (Q_prime_D - HF) / (xD - zF)
    # y - HF = m * (x - zF) => Q_prime_B = m * (xB - zF) + HF
    
    if abs(xD - zF) < 1e-9:
        # xD = zF ise dikey doğru? Distilasyon anlamsız ama kod kırılmasın.
        Q_prime_B = HF - (Q_prime_D - HF) # Simetrik gibi salladım, kritik değil.
    else:
        slope = (Q_prime_D - HF) / (xD - zF)
        Q_prime_B = slope * (xB - zF) + HF
        
    points = {
        'F': (zF, HF),
        'D': (xD, hD),
        'B': (xB, float(f_HL_vs_x(xB))),
        'Delta_D': (xD, Q_prime_D),
        'Delta_B': (xB, Q_prime_B)
    }
    
    # 3. Minimum Reflü Oranı Kontrolü (Ponchon-Savarit)
    # Delta_D noktası (xD, Q'_D) ne kadar yukarıda olmalı?
    # Tie-line'ların uzantısı Delta_D'yi kesmemeli (veya teğet geçmemeli).
    # Özellikle besleme bölgesindeki tie-line (F noktasından geçen veya F ile ilişkili) kritik.
    # Ponchon'da R_min bulmak için F noktasından geçen tie-line'ın uzantısının xD dikey doğrusunu kestiği yere bakılır.
    # Ancak F noktası iki fazlı bölgedeyse F'den geçen tie-line.
    # Tek fazlıysa F'den geçen ve denge eğrisine teğet olan?
    # Basit yaklaşım: Eğer raf sayısı max_trays'e ulaşıyorsa ve x hala xB'ye ulaşmadıysa, muhtemelen R < R_min veya çok yakın.
    
    steps = []
    trays = 0
    max_trays = 100
    
    current_y = xD
    steps.append((current_y, float(f_HV_vs_y(current_y))))
    
    # Pinch point tespiti için önceki x değerlerini takip et
    x_history = [xD]
    
    separation_possible = True
    pinch_detected = False
    
    while trays < max_trays:
        # 1. Denge (Tie-line): y_n -> x_n
        try:
            current_x = float(f_x_vs_y(current_y))
        except:
            separation_possible = False
            break
            
        current_HL = float(f_HL_vs_x(current_x))
        steps.append((current_x, current_HL)) # Sıvı noktası
        
        # Pinch kontrolü: Eğer kompozisyon değişimi çok azsa
        if abs(current_x - x_history[-1]) < 1e-4 and trays > 2:
            pinch_detected = True
            break
            
        x_history.append(current_x)
        trays += 1
        
        if current_x <= xB:
            break
            
        # 2. Operasyon Çizgisi
        if current_x > zF:
            target_point = points['Delta_D']
        else:
            target_point = points['Delta_B']
            
        Xd, Qd = target_point
        
        # Eğim ve yeni y hesabı
        if abs(Xd - current_x) < 1e-9:
            next_y = current_x
        else:
            slope_op = (Qd - current_HL) / (Xd - current_x)
            intercept_op = current_HL - slope_op * current_x
            
            def op_error(y):
                try:
                    hv = float(f_HV_vs_y(y))
                    return hv - (slope_op * y + intercept_op)
                except:
                    return 1e9
            
            try:
                # Bir sonraki y, current_x'ten küçük olmalı (aşağı iniyoruz)
                # Ancak denge eğrisi üzerinde arıyoruz.
                next_y = fsolve(op_error, current_x)[0]
            except:
                separation_possible = False
                break
        
        # Operasyon çizgisi denge eğrisini kesmiyorsa veya yanlış yöne gidiyorsa
        if next_y > current_y: # Ters yön (Normalde y azalmalı)
             pinch_detected = True
             break

        next_HV = float(f_HV_vs_y(next_y))
        steps.append((next_y, next_HV))
        current_y = next_y
        
    if pinch_detected or trays >= max_trays:
        # Ayırma mümkün değil veya R < R_min
        trays = float('inf') 
        
    return df, points, trays, steps

