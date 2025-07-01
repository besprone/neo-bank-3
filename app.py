import streamlit as st
import pandas as pd

from sections.retencion_conversion import retencion_conversion
from sections.resumen_general import resumen_general
from sections.perfil_usuario import perfil_usuario
from sections.churn import churn
# from sections.prediccion_form import prediccion_form

from utils.style_loader import load_css
from utils.load_data import load_or_download_df
from utils.load_data import load_df_resumen_general, load_df_retencion_cohortes

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

# URL de tu archivo en Google Drive
gdrive_url = "https://drive.google.com/uc?id=1pmbNwVEDxSHHeiV-FZBMVXs6MCRjPRix"
# gdrive_url = "https://drive.google.com/uc?id=1CYXR-ZTiIPA7kAovLYNgkXj5AoVjAfEd"


# Llama la función que descarga y carga el DataFrame
try:
    df = load_or_download_df(gdrive_url)
    # st.success("Datos cargados exitosamente.")
    # st.write("Vista previa del DataFrame:", df.head(), df.shape)
except RuntimeError as e:
    st.error(str(e))
    st.stop()

# titulo
st.title("Neo Bank")

# Filtros
df_filtrado = render_filters(df)


tab1, tab2, tab3, tab4, tab5 = render_tabs()

with tab1:
    st.header("🏠 Resumen general")
    # Crear sub-DataFrame solo con las columnas que resumen_general necesita
    df_resumen = load_df_resumen_general()  # tu función que llama BigQuery
    df_retencion_cohortes = load_df_retencion_cohortes() # tu función que llama BigQuery
    resumen_general(df_resumen, df_retencion_cohortes)

with tab2:
    st.header("👥 Perfiles de usuario y uso del producto")
    df_perfil = df_filtrado[[
        'user_id', 'plan', 'converted', 'age_group', 'num_transactions',
        'country', 'lat', 'lon', 'city', 'channel', 'brand_device',
        'user_settings_crypto_unlocked'
    ]].copy()
    perfil_usuario(df_perfil)

with tab3:
    st.header("📊 Retención y conversión de usuarios")
    df_retencion = df_filtrado[['user_id', 'create_date_user', 'create_date_transaction']].copy()
    retencion_conversion(df_retencion)

with tab4:
    st.header("⚠️ Identificación de churn")
    df_churn = df_filtrado[[
        'user_id', 'converted', 'has_notification', 'has_transaction',
        'churned', 'channel', 'plan', 'age_group'
    ]].copy()
    churn(df_churn)

with tab5:
    # Predicción
    st.header("🔮 Simulación de predicción de churn")
    # prediccion_form()

"""
# Churn
st.header("⚠️ Identificación de churn")
churn(df_filtrado)
"""