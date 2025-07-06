import streamlit as st
import pandas as pd
import joblib
from utils.load_data import load_unique_options

modelo = joblib.load('models/best_model2.pkl')

def prediccion_form_2():

    # Inyectar CSS global para el formulario
    st.markdown("""
        <style>
        label p, .stRadio label, .stSelectbox label {
            font-size: 18px !important;
            font-family: 'Arial', sans-serif !important;
        }
        input, select, textarea {
            font-size: 16px !important;
            font-family: 'Arial', sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Traer opciones dinámicas si las necesitas (countries, plans, etc.)
    _, plans, _ = load_unique_options()

    # Layout centrado: 5 columnas
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col3:
        birth_year = st.number_input("Año de nacimiento", min_value=1900, max_value=2025, value=1990)

        user_settings_crypto_unlocked = st.radio(
            "Estado de cripto",
            options=[0, 1],
            format_func=lambda x: "Bloqueado" if x == 0 else "Desbloqueado",
            index=0
        )

        plan = st.selectbox("Plan", sorted(plans))

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
        age = st.number_input("Edad", min_value=0, max_value=120, value=30)
        antiguedad = st.number_input("Antigüedad de la cuenta (en días)", min_value=0, value=0)
        total_transacciones = st.number_input("Total de transacciones", min_value=0, value=0)
        total_monto = st.number_input("Monto total de transacciones (USD)", min_value=0.0, value=0.0)
        promedio_monto = st.number_input("Promedio de monto por transacción (USD)", min_value=0.0, value=0.0)
        nb_transacciones_declinadas = st.number_input("Número de transacciones declinadas", min_value=0, value=0)
        nb_transacciones_reversadas = st.number_input("Número de transacciones reversadas", min_value=0, value=0)
        nb_transacciones_completadas = st.number_input("Número de transacciones completadas", min_value=0, value=0)
        total_notificaciones = st.number_input("Total de notificaciones recibidas", min_value=0, value=0)
        nb_devices = st.number_input("Número de dispositivos asociados", min_value=0, value=0)

        if st.button("Predecir"):
            nuevo_usuario = pd.DataFrame([{
                'birth_year': birth_year,
                'user_settings_crypto_unlocked': user_settings_crypto_unlocked,
                'plan': plan,
                'attributes_notifications_marketing_push': attributes_notifications_marketing_push,
                'attributes_notifications_marketing_email': attributes_notifications_marketing_email,
                'num_contacts': num_contacts,
                'num_referrals': num_referrals,
                'num_successful_referrals': num_successful_referrals,
                'age': age,
                'antiguedad': antiguedad,
                'total_transacciones': total_transacciones,
                'total_monto': total_monto,
                'promedio_monto': promedio_monto,
                'nb_transacciones_declinadas': nb_transacciones_declinadas,
                'nb_transacciones_reversadas': nb_transacciones_reversadas,
                'nb_transacciones_completadas': nb_transacciones_completadas,
                'total_notificaciones': total_notificaciones,
                'nb_devices': nb_devices
            }])

            prediccion = modelo.predict_proba(nuevo_usuario)[0][1]
            st.success(f"Predicción del modelo: {prediccion:.2%} de probabilidad de churn")

        if st.button("Resetear formulario"):
            st.rerun()
