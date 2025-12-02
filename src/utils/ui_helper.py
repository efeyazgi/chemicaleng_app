import streamlit as st
import os

def load_css(file_path="src/assets/style.css"):
    """
    Loads a CSS file and injects it into the Streamlit app.
    """
    try:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback if running from a different directory or file missing
        # Try absolute path based on current file location
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_path = os.path.join(base_dir, "assets", "style.css")
        try:
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"CSS dosyası yüklenemedi: {e}")

def render_header(title, icon=""):
    """
    Renders a styled header with an optional icon.
    """
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 3rem; margin-right: 15px;">{icon}</div>
            <div>
                <h1 style="margin: 0; padding: 0;">{title}</h1>
            </div>
        </div>
        <hr style="margin-top: 5px; margin-bottom: 30px; border: 0; border-top: 2px solid #00ADB5;">
    """, unsafe_allow_html=True)

def render_card(title, value, unit="", description="", color="#00ADB5"):
    """
    Renders a custom card for displaying metrics.
    """
    st.markdown(f"""
        <div class="custom-card" style="border-left: 5px solid {color};">
            <h3 style="color: {color};">{title}</h3>
            <div style="display: flex; align-items: baseline;">
                <span class="value">{value}</span>
                <span class="unit">{unit}</span>
            </div>
            <div style="font-size: 0.9rem; color: #888; margin-top: 5px;">{description}</div>
        </div>
    """, unsafe_allow_html=True)

def render_info_card(text, icon="ℹ️"):
    """
    Renders a simple info card.
    """
    st.markdown(f"""
        <div style="background-color: #E1F5FE; border-left: 5px solid #03A9F4; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 10px;">{icon}</span>
                <span style="color: #0277BD;">{text}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
