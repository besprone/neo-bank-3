import streamlit as st

def render_filters(df):
    st.sidebar.header("🔎 Filtros")

    # País
    paises = sorted(df['country'].dropna().unique())
    pais_seleccionado = st.sidebar.selectbox("Selecciona un país", options=[""] + paises)

    # Plan
    planes = sorted(df['plan'].dropna().unique())
    plan_seleccionado = st.sidebar.selectbox("Selecciona un plan", options=[""] + planes)

    # Rango de edad
    edad_min, edad_max = int(df['age'].min()), int(df['age'].max())
    rango_edad = st.sidebar.slider(
        "Rango de edad", 
        min_value=edad_min, 
        max_value=edad_max, 
        value=(edad_min, edad_max)
    )

    # Canal
    canales = sorted(df['channel'].dropna().unique())
    canal_seleccionado = st.sidebar.selectbox("Selecciona un canal", options=[""] + canales)

    # Estado de churn
    estado_churn = st.sidebar.selectbox(
        "Estado de churn", 
        options=["", "Churned", "No Churned"]
    )

    # Aplicar filtros
    df_filtrado = df.copy()

    if pais_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['country'] == pais_seleccionado]

    if plan_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['plan'] == plan_seleccionado]

    if canal_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['channel'] == canal_seleccionado]

    df_filtrado = df_filtrado[df_filtrado['age'].between(rango_edad[0], rango_edad[1])]

    if estado_churn:
        if estado_churn == "Churned":
            df_filtrado = df_filtrado[df_filtrado['churned'] == True]
        elif estado_churn == "No Churned":
            df_filtrado = df_filtrado[df_filtrado['churned'] == False]

    return df_filtrado
