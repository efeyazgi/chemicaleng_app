import streamlit as st
import time
import datetime
import pyrebase
from extra_streamlit_components import CookieManager
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="ChemCalc - Ana Sayfa",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- COOKIE YÖNETİCİSİ ---
try:
    # Tarayıcı çerezlerini yönetmek için bir anahtar belirler.
    # Bu anahtar, güvenlik için .streamlit/secrets.toml dosyasından okunur.
    cookies = CookieManager(key=st.secrets["cookie_manager_key"])
except Exception as e:
    st.error(f"Cookie yöneticisi başlatılamadı. Hata: {e}")
    st.stop()


# --- FIREBASE YAPILANDIRMASI 
try:
    firebase_config = {
        "apiKey": st.secrets["firebase"]["apiKey"],
        "authDomain": st.secrets["firebase"]["authDomain"],
        "projectId": st.secrets["firebase"]["projectId"],
        "storageBucket": st.secrets["firebase"]["storageBucket"],
        "messagingSenderId": st.secrets["firebase"]["messagingSenderId"],
        "appId": st.secrets["firebase"]["appId"],
        "measurementId": st.secrets["firebase"]["measurementId"],
        "databaseURL": st.secrets["firebase"]["databaseURL"]
    }

    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    st.error(f"Firebase başlatılırken bir hata oluştu. Lütfen .streamlit/secrets.toml dosyanızı kontrol edin. Hata: {e}")
    st.stop()


# --- KİMLİK DOĞRULAMA YARDIMCI FONKSİYONLARI ---
def check_login():
    """Kullanıcının oturum açıp açmadığını kontrol eder."""
    return st.session_state.get("logged_in", False)

def logout():
    """Kullanıcı oturumunu sonlandırır, ilgili çerezi siler ve kontrol bayraklarını sıfırlar."""
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.is_guest = False
    st.session_state.just_logged_out = True
    st.session_state.initial_cookie_check_done = False # Bir sonraki ziyaret için çerez kontrolünü tekrar aktif eder.
    if cookies.get("remember_me_token"):
        cookies.delete("remember_me_token")

def set_guest():
    """Misafir kullanıcı oturumu başlatır."""
    st.session_state.logged_in = True
    st.session_state.is_guest = True
    st.session_state.email = "Misafir"


# --- OTURUM DURUMU (SESSION STATE) İLK DEĞER ATAMALARI ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.is_guest = False
    st.session_state.initial_cookie_check_done = False # Otomatik giriş kontrolünün sadece bir kez yapılmasını sağlar.

# --- "BENİ HATIRLA" ÇEREZ KONTROLÜ ---
# Bu blok, sayfa ilk yüklendiğinde "Beni Hatırla" çerezini kontrol ederek otomatik giriş yapar.
# Manuel girişe müdahale etmemesi için, bir oturum boyunca sadece bir kez çalışır.
just_logged_out = st.session_state.pop('just_logged_out', False)
if not st.session_state.get('initial_cookie_check_done'):
    if not check_login() and not just_logged_out:
        remember_me_token = cookies.get("remember_me_token")
        if remember_me_token:
            try:
                user_session = auth.refresh(remember_me_token)
                user_info = auth.get_account_info(user_session['idToken'])
                email = user_info['users'][0]['email']

                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.is_guest = False

                cookies.set(
                    "remember_me_token",
                    user_session['refreshToken'],
                    expires_at=datetime.datetime.now() + datetime.timedelta(days=30)
                )
                # Otomatik giriş başarılı olduğu için arayüzü güncelle.
                st.rerun()
            except Exception as e:
                # Geçersiz çerez bulunursa sil.
                cookies.delete("remember_me_token")
    # Kontrolün yapıldığını işaretle.
    st.session_state.initial_cookie_check_done = True


# --- ANA UYGULAMA MANTIĞI ---

if not check_login():
    # --- GİRİŞ YAPILMAMIŞ KULLANICI ARAYÜZÜ ---
    st.markdown("<h1 style='text-align: center;'>ChemCalc Hesaplama Platformu</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Devam etmek için lütfen giriş yapın veya kayıt olun.</p>", unsafe_allow_html=True)
    st.markdown("---")

    _ , center_col, _ = st.columns([1, 2, 1])

    with center_col:
        login_tab, register_tab = st.tabs(["Giriş Yap", "Kayıt Ol"])

        with login_tab:
            st.markdown("### 🔐 Giriş Yap")
            with st.form(key="login_form"):
                email = st.text_input("Email")
                password = st.text_input("Şifre", type="password")
                remember_me = st.checkbox("Beni Hatırla")
                submit_button = st.form_submit_button(label="Giriş Yap", use_container_width=True)

                if submit_button:
                    if not email or not password:
                        st.warning("Lütfen email ve şifre alanlarını doldurun.")
                    else:
                        try:
                            user = auth.sign_in_with_email_and_password(email, password)
                            
                            st.session_state.logged_in = True
                            st.session_state.email = email
                            st.session_state.is_guest = False

                            if remember_me:
                                refresh_token = user['refreshToken']
                                cookies.set(
                                    "remember_me_token",
                                    refresh_token,
                                    expires_at=datetime.datetime.now() + datetime.timedelta(days=30)
                                )

                            st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error("Email veya şifre hatalı. Lütfen bilgilerinizi kontrol edin.")

        with register_tab:
            st.markdown("### 🆕 Kayıt Ol")
            with st.form(key="register_form"):
                reg_email = st.text_input("Email Adresiniz", key="reg_email")
                reg_password = st.text_input("Şifre Belirleyin", type="password", key="reg_pass")
                reg_password_confirm = st.text_input("Şifreyi Onaylayın", type="password", key="reg_pass_confirm")
                register_button = st.form_submit_button(label="Kayıt Ol", use_container_width=True)

                if register_button:
                    if not reg_email or not reg_password:
                        st.warning("Lütfen tüm alanları doldurun.")
                    elif reg_password != reg_password_confirm:
                        st.warning("Şifreler eşleşmiyor.")
                    else:
                        try:
                            auth.create_user_with_email_and_password(reg_email, reg_password)
                            st.success("✅ Kayıt başarılı! Artık 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")
                        except Exception as e:
                            st.error(f"❌ Kayıt başarısız. Bu e-posta zaten kullanılıyor olabilir.")

        st.markdown("<p style='text-align: center;'>veya</p>", unsafe_allow_html=True)

        if st.button("👤 Misafir Olarak Devam Et", use_container_width=True):
            set_guest()
            st.rerun()

else:
    # --- GİRİŞ YAPMIŞ KULLANICI ARAYÜZÜ ---
    with st.sidebar:
        st.markdown("### Oturum Bilgisi")
        if st.session_state.is_guest:
            st.info("👤 Misafir modunda geziniyorsunuz.")
        else:
            st.success(f"Hoş geldin,\n**{st.session_state.email}**")

        if st.button("🔒 Oturumu Kapat", use_container_width=True):
            logout()
            st.rerun()
        st.markdown("---")
        st.info("Hesaplamalara sol menüden veya aşağıdaki kartlardan ulaşabilirsiniz.")
        
        st.markdown("<br><br>", unsafe_allow_html=True) # Dikey boşluk
        
        # Logoyu ortalamak ve boyutunu ayarlamak için sütunlar kullanılır.
        # Ortadaki sütunun göreceli genişliği, logonun boyutunu belirler.
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            try:
                st.image("assets/logo.png", use_container_width=True)
            except Exception as e:
                st.warning("Logo dosyası bulunamadı.")

    # --- ANA SAYFA İÇERİĞİ ---
    st.title("ChemCalc Hesaplama Platformu")
    st.caption("Kimya Mühendisliği İçin Hepsi Bir Arada Araç Seti")

    st.markdown("---")
    st.subheader("🔍 Modül Seçimi")
    st.write(
        "Bu platform, kimya mühendisliği öğrencileri ve profesyonelleri için temel mühendislik "
        "hesaplamalarını kolay ve etkileşimli bir biçimde yapmayı amaçlar. Sol menüden veya aşağıdaki "
        "modüllerden seçim yapabilirsiniz."
    )
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("### 🌡️ Termodinamik Özellikler")
            st.write("Saf maddelerin sıcaklık/basınca bağlı özelliklerini hesaplayın.")
            if st.button("Modüle Git", key="thermo", use_container_width=True):
                st.switch_page("pages/00_Termodinamik_Ozellikler.py")

        with st.container(border=True):
            st.markdown("### 🔥 Isı Transferi Hesaplayıcısı")
            st.write("Çok katmanlı düzlem, silindir veya küre ısı transferi.")
            if check_login() and not st.session_state.is_guest:
                if st.button("Modüle Git", key="heat", use_container_width=True):
                    st.switch_page("pages/02_Isı_Transferi.py")
            else:
                st.button("Modüle Git", key="heat_disabled", disabled=True, use_container_width=True)
                st.warning("Bu modül yalnızca kayıtlı kullanıcılar içindir.")

        with st.container(border=True):
            st.markdown("### ⚗️ Ayırma İşlemleri (Distilasyon)")
            st.write("McCabe–Thiele yöntemi ile kolon analizi.")
            if check_login() and not st.session_state.is_guest:
                if st.button("Modüle Git", key="distil", use_container_width=True):
                    st.switch_page("pages/05_Ayırma_İşlemleri.py")
            else:
                st.button("Modüle Git", key="distil_disabled", disabled=True, use_container_width=True)
                st.warning("Bu modül yalnızca kayıtlı kullanıcılar içindir.")

    with col2:
        with st.container(border=True):
            st.markdown("### 💧 Akışkanlar Mekaniği Hesaplayıcısı")
            st.write("Reynolds, sürtünme faktörü ve ΔP hesaplayın.")
            if st.button("Modüle Git", key="fluids", use_container_width=True):
                st.switch_page("pages/01_Akışkanlar_Mekaniği.py")

        with st.container(border=True):
            st.markdown("### ⚛️ Reaksiyon Mühendisliği")
            st.write("Reaktör hacmi, dönüşüm ve süre analizleri.")
            if st.button("Modüle Git", key="reaction", use_container_width=True):
                st.switch_page("pages/03_Reaksiyon_Mühendisliği.py")

        with st.container(border=True):
            st.markdown("### 🌬️ Psikrometrik Hesaplayıcı")
            st.write("Nem oranı, entalpi ve çiğ noktası hesaplayın.")
            if st.button("Modüle Git", key="psychro", use_container_width=True):
                st.switch_page("pages/04_Psikrometri.py")

        with st.container(border=True):
            st.markdown("### 📏 Genel Birim Çevirici")
            st.write("Mühendislik birimleri arasında dönüşüm.")
            if st.button("Modüle Git", key="units", use_container_width=True):
                st.switch_page("pages/06_Birim_Çevirici.py")
