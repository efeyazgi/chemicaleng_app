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
Bu uygulama, kimlik doğrulama ve oturum yönetimi amacıyla sınırlı verileri işler.

- "Beni Hatırla" seçeneği ile kalıcı bir oturum çerezi kullanılabilir.
- Kimlik doğrulama, Firebase hizmeti üzerinden sağlanır; e‑posta adresiniz yalnızca giriş ve hesap oluşturma amacıyla kullanılır.
- Uygulama analitik/izleme çerezi içermez.
- Hesaplama girdileri tarayıcınızda işlenir; sunucuya yalnızca kimlik doğrulama için gerekli minimal veriler iletilir.

Uygulama, **eğitim ve kişisel kullanım** amaçlıdır.
""")
