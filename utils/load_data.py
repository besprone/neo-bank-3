import os
import gdown
import pandas as pd
import streamlit as st
from google.cloud import bigquery

@st.cache_data  # 👈 esta línea es la clave
def load_or_download_df(url: str, local_folder: str = "data", filename: str = "df_sample.csv") -> pd.DataFrame:
    """
    Descarga el archivo CSV desde Google Drive si no existe localmente
    y lo carga como un DataFrame de pandas.
    """
    # Asegura que la carpeta local existe
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
        
    local_path = os.path.join(local_folder, filename)
    
    # Descarga solo si no existe
    if not os.path.exists(local_path):
        print("Descargando archivo desde Google Drive...")
        try:
            gdown.download(url, local_path, quiet=False)
            print("¡Archivo descargado correctamente!")
        except Exception as e:
            raise RuntimeError(f"Error al descargar el archivo: {e}")

    # Lee el archivo CSV
    try:
        df = pd.read_csv(local_path, parse_dates=["create_date_user", "create_date_transaction"])
        print("Datos cargados exitosamente.")
        return df
    except Exception as e:
        raise RuntimeError(f"No se pudo leer el archivo: {e}")

def load_df_resumen_general():
    client = bigquery.Client()
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.resumen_general`
    """
    df = client.query(query).to_dataframe()
    return df

def load_df_retencion_cohortes():
    client = bigquery.Client()
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.retencion_cohortes`
    """
    df = client.query(query).to_dataframe()
    return df

def load_df_perfil_usuario():
    client = bigquery.Client()
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.perfil_usuario`
    """
    df = client.query(query).to_dataframe()
    return df

def load_df_retencion_conversion():
    client = bigquery.Client()
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.retencion_conversion`
    """
    df = client.query(query).to_dataframe()
    return df

def load_df_churn():
    client = bigquery.Client()
    query = """
        SELECT * FROM `numeric-advice-452700-j9.neo_bank_.churn`
    """
    df = client.query(query).to_dataframe()
    return df
