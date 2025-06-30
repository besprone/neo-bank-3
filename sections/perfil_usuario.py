import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

def plan(df):
    # Eliminar duplicados de usuarios
    df_unicos = df.drop_duplicates(subset='user_id')

    # Filtrar solo usuarios que tienen plan definido (no nulo ni vacío)
    df_planes = df_unicos[df_unicos['plan'].notna() & (df_unicos['plan'] != '')]

    # Contar usuarios únicos por tipo de plan
    distribucion_planes = df_planes['plan'].value_counts().reset_index()
    distribucion_planes.columns = ['plan', 'usuarios']

    # Gráfica de barras
    fig_plan = px.bar(
        distribucion_planes,
        x='plan',
        y='usuarios',
        color='plan',
        text='usuarios',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_plan.update_traces(textposition='outside')
    fig_plan.update_layout(xaxis_title='Plan', yaxis_title='Número de usuarios')

    return fig_plan

def distribucion_por_edad(df):
    # Filtrar usuarios con grupo de edad no nulo
    df_edad = df[df['age_group'].notna()]

    # Agrupar por grupo de edad y contar usuarios únicos
    edad_grouped = (
        df_edad.groupby('age_group')['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values(by='usuarios', ascending=False)
    )

    fig_edad = px.bar(
        edad_grouped,
        x='age_group',
        y='usuarios',
        color='age_group',
        labels={'age_group': 'Grupo de edad', 'usuarios': 'Usuarios'},
        color_discrete_sequence=px.colors.sequential.Sunset,
        text='usuarios'
    )

    return fig_edad

def mapa_usuarios_por_pais(df):
    usuarios_por_pais = df.groupby(['country', 'lat', 'lon'])['user_id'].nunique().reset_index()
    usuarios_por_pais.rename(columns={'user_id': 'usuarios'}, inplace=True)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=usuarios_por_pais,
        get_position='[lon, lat]',
        get_radius='usuarios * 70',
        get_fill_color='[0, 100, 250, 150]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=usuarios_por_pais['lat'].mean(),
        longitude=usuarios_por_pais['lon'].mean(),
        zoom=3
    )

    chart = pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{country}: {usuarios} usuarios"},
        
    )

    return chart, usuarios_por_pais

def distribucion_ciudad(df):
    # Agrupar por ciudad y contar usuarios únicos
    usuarios_por_ciudad = (
        df.groupby('city')['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values('usuarios', ascending=False)
    )
    # Filtrar solo las ciudades con más usuarios
    top_ciudades = usuarios_por_ciudad.head(20)
    # visualización
    fig_ciudad = px.bar(
        top_ciudades,
        x='usuarios',
        y='city',
        orientation='h',
        color='usuarios',
        color_continuous_scale='Tealgrn',
        labels={'city': 'Ciudad', 'usuarios': 'Usuarios'},
        text='usuarios'
    )

    return fig_ciudad

def canal(df):
    # Agrupar por canal y contar usuarios únicos
    usuarios_por_canal = (
        df.groupby('channel')['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values('usuarios', ascending=False)
    )
    # Visualizar
    fig_canal = px.bar(
        usuarios_por_canal,
        x='channel',
        y='usuarios',
        color='usuarios',
        labels={'channel': 'Canal de adquisición', 'usuarios': 'Usuarios'},
        color_continuous_scale='burgyl',
        text='usuarios'
    )
    return fig_canal

def devices(df):
    #Agrupar por dispositivo y contar usuarios únicos
    usuarios_por_dispositivo = (
        df.groupby('brand_device')['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values(by='usuarios', ascending=False)
    )
    fig_devices = px.bar(
        usuarios_por_dispositivo,
        x='brand_device',
        y='usuarios',
        labels={'usuarios': 'Usuarios únicos', 'brand_device': 'Dispositivo'},
        color='usuarios',
        color_continuous_scale='darkmint',
        text='usuarios'
    )
    return fig_devices

def transacciones_por_segmento(df):
    # Agrupar por usuario para obtener una fila por user_id con su edad y total de transacciones
    group_usuarios_unicos = df.groupby('user_id').agg({
        'age_group': 'first',
        'num_transactions': 'first'  # o 'sum', dependiendo cómo esté el dato original
    }).reset_index()

    # Ahora agrupar por grupo de edad
    transacciones_por_edad = group_usuarios_unicos.groupby('age_group')['num_transactions'].sum().reset_index()

    # Crear gráfico de barras
    fig_txn_segmento = px.bar(
        transacciones_por_edad,
        x='age_group',
        y='num_transactions',
        labels={'age_group': 'Grupo de edad', 'num_transactions': 'Total de transacciones'},
        color='num_transactions',
        color_continuous_scale='viridis',
        text='num_transactions'
    )
    return fig_txn_segmento

def conversion_segmento(df):
    usuarios_unicos = df.drop_duplicates(subset='user_id')

    # Agrupar por plan y calcular métricas de conversión
    conversion_por_plan = usuarios_unicos.groupby('plan')['converted'].agg(['count', 'sum']).reset_index()
    conversion_por_plan['conversion_rate'] = round((conversion_por_plan['sum'] / conversion_por_plan['count']) * 100, 2)

    # Ordenar por tasa de conversión descendente
    conversion_por_plan = conversion_por_plan.sort_values(by='conversion_rate', ascending=False)

    # Graficar
    fig_conversion_segmento = px.bar(
        conversion_por_plan,
        x='plan',
        y='conversion_rate',
        labels={'conversion_rate': '% de conversión', 'plan': 'Tipo de plan'},
        text='conversion_rate',
        color='conversion_rate',
        color_continuous_scale='gnbu'
    )

    return fig_conversion_segmento

def uso_crypto(df):
    # Agrupar por uso de cripto y contar usuarios únicos
    uso_crypto = df.groupby('user_settings_crypto_unlocked')['user_id'].nunique().reset_index()
    uso_crypto.columns = ['Crypto habilitado', 'Usuarios únicos']
    # Convertir valores a etiquetas legibles
    uso_crypto['Crypto habilitado'] = uso_crypto['Crypto habilitado'].map({
        'True': 'Sí',
        'False': 'No',
        True: 'Sí',
        False: 'No'
    })
    fig_crypto = px.pie(
        uso_crypto,
        values='Usuarios únicos',
        names='Crypto habilitado',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    return fig_crypto

def perfil_usuario(df):
    
    fig_plan = plan(df)
    fig_edad = distribucion_por_edad(df)
    chart, datos = mapa_usuarios_por_pais(df)
    fig_ciudad = distribucion_ciudad(df)
    fig_canal = canal(df)
    fig_devices = devices(df)
    fig_txn_segmento = transacciones_por_segmento(df)
    fig_conversion_segmento = conversion_segmento(df)
    fig_crypto = uso_crypto(df)


    col1, col2, col3 = st.columns(3)
    col1_1, col1_2, col1_3 = st.columns(3)
    col2_1, col2_2, col2_3 = st.columns(3)
    col3_1, col3_2, col3_3 = st.columns(3)

    with col1:
        with col1_1:
            # Histograma
            st.subheader('Usuarios por plan')
            st.plotly_chart(fig_plan, use_container_width=True)
        with col1_2:
            # Histograma
            st.subheader('Grupo de edad')
            st.plotly_chart(fig_edad, use_container_width=True)
        with col1_3:
            # mapa
            st.subheader("Usuarios por país")
            st.pydeck_chart(chart, use_container_width=True)

    with col2:
        with col2_1:
            # ciudad
            st.subheader('Top 20 ciudades con más usuarios')
            st.plotly_chart(fig_ciudad, use_container_width=True)
        with col2_2:
            # canal
            st.subheader('Usuarios por canal')
            st.plotly_chart(fig_canal, use_container_width=True)
        with col2_3:
            # devices
            st.subheader('Usuarios por tipo de dispositivo')
            st.plotly_chart(fig_devices, use_container_width=True)

    with col3:
        with col3_1:
            # transacción por segmento
            st.subheader('Transacciones por grupo de edad')
            st.plotly_chart(fig_txn_segmento, use_container_width=True)
        with col3_2:
            # conversion por tipo de plan
            st.subheader('% de conversión por tipo de plan')
            st.plotly_chart(fig_conversion_segmento, use_container_width=True)
        with col3_3:
            # uso de crypto
            st.subheader('Funcionalidad cripto activada')
            st.plotly_chart(fig_crypto, use_container_width=True)

    

        