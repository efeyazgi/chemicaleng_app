import streamlit as st

st.set_page_config(page_title="Bilgilendirme", page_icon="📚")

st.title("📚 Bilgilendirme")

secim = st.radio("Görüntülemek istediğiniz bölüm:", ["ℹ️ Hakkında", "🔒 Gizlilik Politikası"])

if secim == "ℹ️ Hakkında":
    st.subheader("Hakkında")
    st.markdown("""
**Kimya Hesap**, kimya mühendisliği öğrencileri ve profesyonelleri için geliştirilmiş açık kaynaklı bir hesaplama ve analiz platformudur.

Bu uygulama:
- Termodinamik özellikler
- Akışkanlar mekaniği
- Isı transferi
- Reaksiyon mühendisliği
- Psikrometri
- Ayırma işlemleri (McCabe–Thiele)
- Birim dönüştürücü

gibi araçları içerir.

**Geliştirici:** [Efe Yazgı](https://github.com/efeyazgi)  
**Üniversite:** Eskişehir Osmangazi Üniversitesi – Kimya Mühendisliği  
**İletişim:** [LinkedIn Profilim](https://www.linkedin.com/in/efeyazgi/)
""")

elif secim == "🔒 Gizlilik Politikası":
    st.subheader("Gizlilik Politikası")
    st.markdown("""
Bu uygulama kullanıcıların **hiçbir kişisel verisini toplamaz**.

- **Çerez veya izleyici içermez.**
- **Veriler yalnızca geçici olarak cihazınızda işlenir.**
- **Sunucuya veri gönderimi yapılmaz.**

Uygulama, tamamen **eğitim ve kişisel kullanım amaçlıdır**.  
Hiçbir ticari veya veri toplama faaliyeti içermez.
""")
