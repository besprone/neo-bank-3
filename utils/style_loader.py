# utils/style_loader.py

import streamlit as st

def load_css(file_path):
    """Carga un archivo CSS y lo inyecta en el HTML de Streamlit."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
