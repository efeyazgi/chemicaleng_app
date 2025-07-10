# ChemCalc - Kimya Mühendisliği Hesaplama Platformu

## 📋 Açıklama

**ChemCalc**, kimya mühendisliği öğrencileri ve profesyonelleri için geliştirilmiş interaktif bir hesaplama platformudur. Termodinamikten reaksiyon mühendisliğine, akışkanlar mekaniğinden psikrometriye kadar birçok temel mühendislik modülünü tek çatı altında sunar.

Bu uygulama hem **yerelde** çalıştırılabilir hem de herhangi bir kurulum gerektirmeden aşağıdaki bağlantıdan doğrudan kullanılabilir:

🔗 [Streamlit Cloud Üzerinden Uygulamayı Açın](https://chemcalc.streamlit.app)

---

## ⚙️ Özellikler

* 🌡️ **Termodinamik Özellikler** – Saf maddeler veya karışımların yoğunluk, viskozite, ısı kapasitesi vb. özelliklerini hesaplayın.
* 🔥 **Isı Transferi** – Çok katmanlı düzlem duvarlarda ısı transfer hızı ve ısıl direnci hesaplayın.
* 💧 **Akışkanlar Mekaniği** – Reynolds sayısı, sürtünme faktörü, basınç düşüşü gibi hesaplamalar.
* ⚛️ **Reaksiyon Mühendisliği** – CSTR, PFR ve batch reaktörlerde hacim ve süre hesapları.
* 🌬️ **Psikrometri** – Çiğ noktası, yaş termometre, nem oranı ve entalpi hesapları.
* ⚗️ **Ayırma İşlemleri (Distilasyon)** – McCabe-Thiele yöntemiyle teorik raf sayısı ve diyagram.
* 📏 **Birim Çevirici** – Uzunluk, sıcaklık, basınç gibi birimler arasında dönüşüm.

---

## 🚀 Kurulum (Yerel Kullanım için)

### Gereksinimler

* Python 3.8 veya üzeri
* Git

### Kurulum Adımları

```bash
# Depoyu klonlayın
git clone https://github.com/efeyazgi/chemicaleng_app.git
cd chemicaleng_app

# Sanal ortam oluşturun (opsiyonel)
python -m venv venv
# Windows için:
venv\Scripts\activate
# macOS/Linux için:
source venv/bin/activate

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### Uygulamayı Başlatma

```bash
streamlit run Home.py
```

Tarayıcıda otomatik olarak `http://localhost:8501` açılır.

---

## 📂 Proje Yapısı

```
├── pages/                  # Streamlit sayfa dosyaları
├── src/calculators/        # Hesaplama fonksiyonları
├── Home.py                 # Ana sayfa
├── requirements.txt        # Gereken Python kütüphaneleri
└── README.md               # Proje açıklaması
```

---

## ✅ Testler

```bash
pytest
```

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Yeni bir dal oluşturun (`git checkout -b feature/ozellik`)
3. Değişikliklerinizi commit'leyin (`git commit -m "özellik eklendi"`)
4. Fork'unuza push edin (`git push origin feature/ozellik`)
5. Pull request oluşturun

Lütfen `develop` branch'ine katkıda bulunun ve kodlarınızı `black` ve `flake8` ile formatlayın.

---

## 📄 Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

Platformda kullanılan bazı hesaplama bileşenleri Caleb Bell tarafından geliştirilen `thermo`, `ht`, `fluids` gibi kütüphanelere dayanmaktadır ve aynı şekilde MIT lisansı altındadır.

---
