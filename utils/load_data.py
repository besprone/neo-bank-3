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

    # Traer el mapping country_code → country_name
    catalog_query = """
        SELECT country AS country_code, country_name
        FROM `numeric-advice-452700-j9.neo_bank_.country_coordinates`
    """
    catalog_df = client.query(catalog_query).to_dataframe()

    # Traer pares país-código → ciudad y planes desde users
    users_query = """
        SELECT DISTINCT country AS country_code, city, plan
        FROM `numeric-advice-452700-j9.neo_bank_.users`
        WHERE country IS NOT NULL AND city IS NOT NULL
    """
    users_df = client.query(users_query).to_dataframe()

    # Merge: para obtener el nombre legible del país
    merged_df = users_df.merge(catalog_df, on="country_code", how="left")

    # Sacar lista única de países legibles
    countries = sorted(merged_df['country_name'].dropna().unique().tolist())

    # Sacar planes únicos
    plans = sorted(merged_df['plan'].dropna().unique().tolist())

    # Construir diccionario país legible → lista de ciudades
    country_cities = {}
    for country in countries:
        cities = merged_df.loc[merged_df['country_name'] == country, 'city'].dropna().unique().tolist()
        country_cities[country] = sorted(cities)

    return countries, plans, country_cities



