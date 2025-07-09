# ChemE Pro - Kimya Mühendisliği Hesaplama Platformu

## 📋 Açıklama

ChemE Pro, Streamlit tabanlı, kimya mühendisliği öğrencileri ve profesyonelleri için temel hesaplamaları tek bir çatı altında toplayan etkileşimli bir platformdur. Termodinamikten reaksiyon mühendisliğine, akışkanlar mekaniğinden psikrometriye kadar yaygın kullanılan tüm hesaplama modüllerini içerir.# ChemE Pro - Kimya Mühendisliği Hesaplama Platformu

## 📋 Açıklama

ChemE Pro, Streamlit tabanlı, kimya mühendisliği öğrencileri ve profesyonelleri için temel hesaplamaları tek bir çatı altında toplayan etkileşimli bir platformdur. Termodinamikten reaksiyon mühendisliğine, akışkanlar mekaniğinden psikrometriye kadar yaygın kullanılan tüm hesaplama modüllerini içerir.

---

## ⚙️ Özellikler

* **Termodinamik Özellikler**: Saf maddeler veya karışımların yoğunluk, viskozite, ısı kapasitesi gibi termodinamik ve taşıma özelliklerini hesaplayın ve grafiğini oluşturun.
* **Isı Transferi**: Çok katmanlı düzlem duvarlarda kondüksiyon ve konveksiyon ile ısı transferi hızı ve ısıl direnci hesaplayın.
* **Akışkanlar Mekaniği**: Reynolds sayısı, sürtünme faktörü ve Darcy-Weisbach denklemi ile basınç düşüşünü hesaplayın.
* **Reaksiyon Mühendisliği**: CSTR/PFR reaktör hacimlerini, teorik verimi ve sınırlayıcı bileşen analizini gerçekleştirin.
* **Psikrometri**: Nemli havanın çiğ noktası, mutlak nem, entalpi ve yaş termometre sıcaklığı gibi özelliklerini hesaplayın.
* **Ayırma İşlemleri (Distilasyon)**: McCabe-Thiele metoduyla teorik raf sayısını ve kolon analizini yapın.
* **Birim Çevirici**: Uzunluk, basınç, sıcaklık vb. mühendislik birimlerini hızla dönüştürün.

---

## 🚀 Başlangıç

Aşağıdaki adımları izleyerek projeyi yerel makinelerde çalıştırabilirsiniz.

### Gereksinimler

* Python 3.8 veya üzeri
* Git

### Kurulum

```bash
# Depoyu klonlayın
git clone https://github.com/efeyazgi/chemicaleng_app.git
cd chemicaleng_app

# Sanal ortam oluşturup etkinleştirin (opsiyonel)
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Gerekli paketleri yükleyin
pip install -r requirements.txt
```

### Çalıştırma

```bash
streamlit run Home.py
```

Tarayıcınızda `http://localhost:8501` adresine giderek uygulamaya erişebilirsiniz.

---

## 🗂️ Proje Yapısı

```
├── .devcontainer/          # Geliştirme ortamı (Docker, VS Code ayarları)
├── pages/                  # Streamlit sayfa modülleri
├── src/calculators/        # Hesaplama fonksiyonları ve işlevler
├── tests/                  # Birim testleri
├── Home.py                 # Ana sayfa ve navigasyon
├── requirements.txt        # Proje bağımlılıkları
├── README.md               # Proje tanıtımı
└── .gitignore              # Git takip dışı dosyalar
```

---

## ✅ Testler

```bash
# Tüm testleri çalıştırmak için
pytest
```

---

## 🤝 Katkıda Bulunma

1. Projeyi fork’layın
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m "Yeni özellik ekleme"`)
4. Fork’unuza push edin (`git push origin feature/yeni-ozellik`)
5. Pull request oluşturun

Lütfen `develop` branch’ine katkıda bulunun ve kod standartlarına uygunluk göstermek için `flake8` ve `black` kontrolleri yapın.

---

## 📄 Lisans

Bu proje MIT lisansı altında yayımlanmaktadır.
Orijinal MIT lisans metni ve telif hakkı bildirimi için `LICENSE` dosyasına bakınız.

Projede kullanılan ve Caleb Bell tarafından sağlanan bazı kod parçaları da MIT lisansı ile lisanslanmıştır. Bu kod parçalarındaki telif hakkı ve izin bildirimleri, ilgili kaynak dosyalarının en üstünde korunmuştur.

---


---

## ⚙️ Özellikler

* **Termodinamik Özellikler**: Saf maddeler veya karışımların yoğunluk, viskozite, ısı kapasitesi gibi termodinamik ve taşıma özelliklerini hesaplayın ve grafiğini oluşturun.
* **Isı Transferi**: Çok katmanlı düzlem duvarlarda kondüksiyon ve konveksiyon ile ısı transferi hızı ve ısıl direnci hesaplayın.
* **Akışkanlar Mekaniği**: Reynolds sayısı, sürtünme faktörü ve Darcy-Weisbach denklemi ile basınç düşüşünü hesaplayın.
* **Reaksiyon Mühendisliği**: CSTR/PFR reaktör hacimlerini, teorik verimi ve sınırlayıcı bileşen analizini gerçekleştirin.
* **Psikrometri**: Nemli havanın çiğ noktası, mutlak nem, entalpi ve yaş termometre sıcaklığı gibi özelliklerini hesaplayın.
* **Ayırma İşlemleri (Distilasyon)**: McCabe-Thiele metoduyla teorik raf sayısını ve kolon analizini yapın.
* **Birim Çevirici**: Uzunluk, basınç, sıcaklık vb. mühendislik birimlerini hızla dönüştürün.

---

## 🚀 Başlangıç

Aşağıdaki adımları izleyerek projeyi yerel makinelerde çalıştırabilirsiniz.

### Gereksinimler

* Python 3.8 veya üzeri
* Git

### Kurulum

```bash
# Depoyu klonlayın
git clone https://github.com/efeyazgi/chemicaleng_app.git
cd chemicaleng_app

# Sanal ortam oluşturup etkinleştirin (opsiyonel)
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Gerekli paketleri yükleyin
pip install -r requirements.txt
```

### Çalıştırma

```bash
streamlit run Home.py
```

Tarayıcınızda `http://localhost:8501` adresine giderek uygulamaya erişebilirsiniz.

---

## 🗂️ Proje Yapısı

```
├── .devcontainer/          # Geliştirme ortamı (Docker, VS Code ayarları)
├── pages/                  # Streamlit sayfa modülleri
├── src/calculators/        # Hesaplama fonksiyonları ve işlevler
├── tests/                  # Birim testleri
├── Home.py                 # Ana sayfa ve navigasyon
├── requirements.txt        # Proje bağımlılıkları
├── README.md               # Proje tanıtımı
└── .gitignore              # Git takip dışı dosyalar
```

---

## ✅ Testler

```bash
# Tüm testleri çalıştırmak için
pytest
```

---

## 🤝 Katkıda Bulunma

1. Projeyi fork’layın
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m "Yeni özellik ekleme"`)
4. Fork’unuza push edin (`git push origin feature/yeni-ozellik`)
5. Pull request oluşturun

Lütfen `develop` branch’ine katkıda bulunun ve kod standartlarına uygunluk göstermek için `flake8` ve `black` kontrolleri yapın.

---

## 📄 Lisans

Bu proje MIT lisansı altında yayımlanmaktadır.
Orijinal MIT lisans metni ve telif hakkı bildirimi için `LICENSE` dosyasına bakınız.

Projede kullanılan ve Caleb Bell tarafından sağlanan bazı kod parçaları da MIT lisansı ile lisanslanmıştır. Bu kod parçalarındaki telif hakkı ve izin bildirimleri, ilgili kaynak dosyalarının en üstünde korunmuştur.

---
