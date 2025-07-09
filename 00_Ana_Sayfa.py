import streamlit as st

st.set_page_config(page_title="ChemCalc - Ana Sayfa", page_icon="🧪", layout="wide")

# Logo ve Başlık
col1, col2 = st.columns([1, 4], gap="medium", vertical_alignment="center")

with col1:
    st.image("assets/logo.png", width=150)

with col2:
    st.markdown("<h1 style='margin-bottom: 0; margin-top:0;'>ChemCalc Hesaplama Platformuna Hoş Geldiniz!</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top: 0.2rem; color: gray;'>Kimya Mühendisliği İçin Hepsi Bir Arada Araç Seti</h4>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🔍 Modül Seçimi")

# Açıklama
st.write(
    "Bu platform, kimya mühendisliği öğrencileri ve profesyonelleri için temel mühendislik hesaplamalarını "
    "kolay ve etkileşimli bir biçimde yapmayı amaçlar. Sol menüden veya aşağıdaki modüllerden seçim yaparak kullanabilirsiniz."
)
st.markdown("---")

# Modül Kartları
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.markdown("### 🌡️ Termodinamik Özellikler")
        st.write("Saf maddelerin veya karışımların sıcaklık ve basınca bağlı termodinamik ve taşıma özelliklerini hesaplayın.")
        if st.button("Termodinamik Modülüne Git", key="thermo", use_container_width=True):
            st.switch_page("pages/00_Termodinamik_Ozellikler.py")

    with st.container(border=True):
        st.markdown("### 🔥 Isı Transferi Hesaplayıcısı")
        st.write("Düzlem, silindirik veya küresel yapılar için ısı transferini hesaplayın.")
        if st.button("Isı Transferi Modülüne Git", key="heat", use_container_width=True):
            st.switch_page("pages/02_Isı_Transferi.py")

    with st.container(border=True):
        st.markdown("### ⚗️ Ayırma İşlemleri (Distilasyon)")
        st.write("McCabe-Thiele yöntemi ile distilasyon kolonlarını analiz edin.")
        if st.button("Ayırma İşlemleri Modülüne Git", key="distil", use_container_width=True):
            st.switch_page("pages/05_Ayırma_İşlemleri.py")

with col2:
    with st.container(border=True):
        st.markdown("### 💧 Akışkanlar Mekaniği Hesaplayıcısı")
        st.write("Boru içi akışlar için Reynolds sayısı ve basınç düşüşü hesaplamaları yapın.")
        if st.button("Akışkanlar Mekaniği Modülüne Git", key="fluids", use_container_width=True):
            st.switch_page("pages/01_Akışkanlar_Mekaniği.py")

    with st.container(border=True):
        st.markdown("### ⚛️ Reaksiyon Mühendisliği")
        st.write("Reaktör hacmi, dönüşüm ve süre hesaplamaları gerçekleştirin.")
        if st.button("Reaksiyon Müh. Modülüne Git", key="reaction", use_container_width=True):
            st.switch_page("pages/03_Reaksiyon_Mühendisliği.py")

    with st.container(border=True):
        st.markdown("### 🌬️ Psikrometrik Hesaplayıcı")
        st.write("Nemli havanın entalpi, nem oranı, çiğ noktası gibi özelliklerini hesaplayın.")
        if st.button("Psikrometri Modülüne Git", key="psychro", use_container_width=True):
            st.switch_page("pages/04_Psikrometri.py")

    with st.container(border=True):
        st.markdown("### 📏 Genel Birim Çevirici")
        st.write("Sık kullanılan mühendislik birimlerini dönüştürün.")
        if st.button("Birim Çeviriciye Git", key="units", use_container_width=True):
            st.switch_page("pages/06_Birim_Çevirici.py")
