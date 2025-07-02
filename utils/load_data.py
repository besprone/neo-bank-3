import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import bigquery

# ⬇️ Leer las credenciales desde st.secrets y crear objeto credentials solo UNA vez
credentials_dict = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

@st.cache_data
def load_df_resumen_general():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.resumen_general`
    """
    df = client.query(query).to_dataframe()
    return df

@st.cache_data
def load_df_retencion_cohortes():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.retencion_cohortes`
    """
    df = client.query(query).to_dataframe()
    return df

@st.cache_data
def load_df_perfil_usuario():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.perfil_usuario`
    """
    df = client.query(query).to_dataframe()
    return df

@st.cache_data
def load_df_retencion_conversion():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.retencion_conversion`
    """
    df = client.query(query).to_dataframe()
    return df

@st.cache_data
def load_df_churn():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.churn`
    """
    df = client.query(query).to_dataframe()
    return df
