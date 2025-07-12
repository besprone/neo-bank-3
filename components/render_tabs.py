# components/render_tabs.py

import streamlit as st

def render_tabs():
    return st.tabs(
        [
            "Resumen general", 
            "Perfiles de usuario", 
            "Retención y conversión",
            'Engagement',
            "Churn", 
            'Predicción de churn'
        ]
    )
