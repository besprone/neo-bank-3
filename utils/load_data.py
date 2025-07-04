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

@st.cache_data
def load_unique_options():
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    
    query = """
        SELECT 
            ARRAY_AGG(DISTINCT country IGNORE NULLS) AS countries,
            ARRAY_AGG(DISTINCT city IGNORE NULLS) AS cities,
            ARRAY_AGG(DISTINCT plan IGNORE NULLS) AS plans
        FROM `numeric-advice-452700-j9.neo_bank_.users`
    """
    df = client.query(query).to_dataframe()
    
    # Extrae los arrays de la fila única que devuelve
    countries = df['countries'][0]
    cities = df['cities'][0]
    plans = df['plans'][0]
    
    return countries, cities, plans

