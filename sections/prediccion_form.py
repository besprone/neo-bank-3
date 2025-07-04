import streamlit as st
import pandas as pd
import joblib
from utils.load_data import load_unique_options

modelo = joblib.load('models/modelo_churn.pkl')

def prediccion_form():
    countries, cities, plans = load_unique_options()

    # Layout centrado: 5 columnas
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col3:
        birth_year = st.number_input("Año de nacimiento", min_value=1900, max_value=2025, value=1990)
        country = st.selectbox("País", sorted(countries))
        city = st.selectbox("Ciudad", sorted(cities))
        plan = st.selectbox("Plan", sorted(plans))

        user_settings_crypto_unlocked = st.radio(
            "Estado de cripto",
            options=[0, 1],
            format_func=lambda x: "Bloqueado" if x == 0 else "Desbloqueado",
            index=0
        )

        attributes_notifications_marketing_push = st.radio(
            "Preferencia de notificaciones push",
            options=[0.0, 1.0],
            format_func=lambda x: "Desactivado" if x == 0.0 else "Activado",
            index=0
        )

        attributes_notifications_marketing_email = st.radio(
            "Preferencia de notificaciones email",
            options=[0.0, 1.0],
            format_func=lambda x: "Desactivado" if x == 0.0 else "Activado",
            index=0
        )

        num_contacts = st.number_input("Número de contactos", min_value=0, value=0)
        num_referrals = st.number_input("Número de referidos", min_value=0, value=0)
        num_successful_referrals = st.number_input("Número de referidos exitosos", min_value=0, value=0)
        num_transactions = st.number_input("Número de transacciones", min_value=0, value=0)
        num_notifications = st.number_input("Número de notificaciones recibidas", min_value=0, value=0)

        converted = st.radio(
            "¿Estado de conversión?",
            options=[0, 1],
            format_func=lambda x: "No convertido" if x == 0 else "Convertido",
            index=0
        )

        if st.button("Predecir"):
            nuevo_usuario = pd.DataFrame([{
                'birth_year': birth_year,
                'country': country,
                'city': city,
                'user_settings_crypto_unlocked': user_settings_crypto_unlocked,
                'plan': plan,
                'attributes_notifications_marketing_push': attributes_notifications_marketing_push,
                'attributes_notifications_marketing_email': attributes_notifications_marketing_email,
                'num_contacts': num_contacts,
                'num_referrals': num_referrals,
                'num_successful_referrals': num_successful_referrals,
                'num_transactions': num_transactions,
                'num_notifications': num_notifications,
                'converted': converted
            }])

            prediccion = modelo.predict(nuevo_usuario)
            st.success(f"**¿El usuario es churn?:** {'Sí' if prediccion[0] == 1 else 'No'}")
            # st.rerun()  # Reinicia la app y limpia los campos del formulario

        # Botón para reiniciar el formulario
        if st.button("Resetear formulario"):
            st.rerun()
