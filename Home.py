import streamlit as st

st.set_page_config(
    page_title="ChemE Pro - Ana Sayfa",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 ChemE Pro Hesaplama Platformuna Hoş Geldiniz!")
st.markdown("---")
st.subheader("Mühendislik Hesaplamalarınızı Kolaylaştırmak İçin Tasarlandı")
st.write(
    "Bu platform, kimya mühendisliği öğrencilerinin ve profesyonellerinin ihtiyaç duyduğu temel hesaplamaları "
    "tek bir çatı altında toplayan, interaktif ve kullanıcı dostu bir araç setidir. "
    "Sol taraftaki menüden istediğiniz hesaplama modülüne ulaşabilirsiniz."
)
st.markdown("---")

st.subheader("Kullanılabilir Araçlar")

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.markdown("### 🌡️ Termodinamik Özellikler")
        st.write("Saf maddelerin veya karışımların sıcaklık ve basınca bağlı termodinamik ve taşıma özelliklerini (yoğunluk, viskozite, ısı kapasitesi vb.) hesaplayın ve grafiğini çizin.")
        if st.button("Termodinamik Modülüne Git", key="thermo", use_container_width=True):
            st.switch_page("pages/00_Termodinamik_Ozellikler.py")

    with st.container(border=True):
        st.markdown("### 🔥 Isı Transferi Hesaplayıcısı")
        st.write("Çok katmanlı düzlem duvarlarda kondüksiyon ve konveksiyon ile ısı transferi hızını ve ısıl direnci hesaplayın. Katmanları dinamik olarak yönetin.")
        if st.button("Isı Transferi Modülüne Git", key="heat", use_container_width=True):
            st.switch_page("pages/02_Isı_Transferi.py")

with col2:
    with st.container(border=True):
        st.markdown("### 💧 Akışkanlar Mekaniği Hesaplayıcısı")
        st.write("Boru içi akışlar için Reynolds sayısı, sürtünme faktörü ve Darcy-Weisbach denklemi ile basınç düşüşü gibi temel hesaplamaları yapın.")
        if st.button("Akışkanlar Mekaniği Modülüne Git", key="fluids", use_container_width=True):
            st.switch_page("pages/01_Akışkanlar_Mekaniği.py")

    with st.container(border=True):
        st.markdown("### ⚛️ Reaksiyon Mühendisliği Hesaplayıcısı")
        st.write("Verilen denkleştirilmiş reaksiyonlar için sınırlayıcı bileşeni, teorik verimi ve CSTR/PFR reaktör hacimlerini hesaplayın.")
        if st.button("Reaksiyon Müh. Modülüne Git", key="reaction", use_container_width=True):
            st.switch_page("pages/03_Reaksiyon_Mühendisliği.py")

    with st.container(border=True):
        st.markdown("### 🌬️ Psikrometrik Hesaplayıcı")
        st.write("Nemli havanın çiğ noktası, mutlak nem, entalpi ve yaş termometre sıcaklığı gibi termodinamik özelliklerini hesaplayın.")
        if st.button("Psikrometri Modülüne Git", key="psychro", use_container_width=True):
            st.switch_page("pages/04_Psikrometri.py")
            
with col1:
    with st.container(border=True):
        st.markdown("### ⚗️ Ayırma İşlemleri (Distilasyon)")
        st.write("İkili karışımlar için McCabe-Thiele metodunu kullanarak distilasyon kolonlarını analiz edin ve teorik raf sayısını bulun.")
        if st.button("Ayırma İşlemleri Modülüne Git", key="distil", use_container_width=True):
            st.switch_page("pages/05_Ayırma_İşlemleri.py")

with col2:
    with st.container(border=True):
        st.markdown("### 📏 Genel Birim Çevirici")
        st.write("Uzunluk, basınç, sıcaklık ve daha birçok mühendislik birimini kolayca birbirine dönüştürün.")
        if st.button("Birim Çeviriciye Git", key="units", use_container_width=True):
            st.switch_page("pages/06_Birim_Çevirici.py")
