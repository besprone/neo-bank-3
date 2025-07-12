import streamlit as st
import pandas as pd

from sections.retencion_conversion import retencion_conversion
from sections.resumen_general import resumen_general
from sections.perfil_usuario import perfil_usuario
from sections.churn import churn
from sections.prediccion_form import prediccion_form
from sections.prediccion_form_2 import prediccion_form_2
from sections.engagement import engagement

from utils.style_loader import load_css
from utils.load_data import load_df_resumen_general, load_df_retencion_cohortes, load_df_perfil_usuario, load_df_retencion_conversion, load_df_churn, load_df_engagement_con_churn

from components.render_tabs import render_tabs
from components.render_filters import render_filters

st.set_page_config(
    page_title="Neo Bank - Overview",
    page_icon="📊",
    layout="wide"  # 👈 esto es lo que importa
)

# Carga de múltiples archivos de estilos
load_css("styles/tabs.css")
load_css("styles/metric.css")
load_css("styles/sidebar.css")

# titulo
st.title("Neo Bank")

# # Filtros
# df_filtrado = render_filters(df)

tab1, tab2, tab3, tab4, tab5, tab6 = render_tabs()

with tab1:
    st.header("🏠 Resumen general")
    # Crear sub-DataFrame solo con las columnas que resumen_general necesita
    df_resumen = load_df_resumen_general()  # tu función que llama BigQuery
    df_retencion_cohortes = load_df_retencion_cohortes() # tu función que llama BigQuery
    resumen_general(df_resumen, df_retencion_cohortes)

with tab2:
    st.header("👥 Perfiles de usuario y uso del producto")
    df_perfil = load_df_perfil_usuario()
    perfil_usuario(df_perfil)

with tab3:
    st.header("📊 Retención y conversión de usuarios")
    df_retencion = load_df_retencion_conversion()
    retencion_conversion(df_retencion)

with tab4:
    st.header("👥 Engagement")
    df_engagement_churn = load_df_engagement_con_churn()
    engagement(df_engagement_churn)

with tab5:
    st.header("⚠️ Identificación de churn")
    df_churn = load_df_churn()
    churn(df_churn)

with tab6:
    st.markdown("<h2 style='text-align: center;'>🔮 Simulación de predicción de churn</h2>", unsafe_allow_html=True)
    prediccion_form_2()



