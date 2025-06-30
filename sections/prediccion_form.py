import streamlit as st
import pandas as pd

# Supongamos que este es tu dataframe de features (X)
# Aquí sólo un ejemplo con columnas ficticias:

df = pd.read_csv('../data/df_all_data.csv')

X = pd.DataFrame(columns=[
    'num_contacts', 'num_referrals', 'num_transactions',
    'attributes_notifications_marketing_push', 'plan', 'country'
])

with st.form("prediction_form"):
    st.write("Introduce los valores de las características:")

    # Diccionario para guardar los inputs
    inputs = {}

    for col in X.columns:
        # Genera un input diferente según el tipo de columna (numérica o categórica)
        if col in ['plan', 'country']:
            # Para columnas categóricas, usa un text input o un select si conoces las opciones
            inputs[col] = st.text_input(f"{col} (texto/categoría)")
        else:
            # Para numéricas, usa number_input
            inputs[col] = st.number_input(f"{col} (numérico)", value=0.0)

    # Botón de predicción
    submitted = st.form_submit_button("Predecir")

if submitted:
    st.subheader("Valores ingresados:")
    st.write(inputs)
    # Aquí podrías transformar `inputs` en un DataFrame de una fila para pasarlo al modelo:
    # ejemplo: modelo.predict(pd.DataFrame([inputs]))
