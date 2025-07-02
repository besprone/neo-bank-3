import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

def plan(df):
    df_unicos = df.drop_duplicates(subset='user_id')
    df_planes = df_unicos[df_unicos['plan'].notna() & (df_unicos['plan'] != '')]
    distribucion_planes = df_planes['plan'].value_counts().reset_index()
    distribucion_planes.columns = ['plan', 'usuarios']
    fig_plan = px.bar(
        distribucion_planes, x='plan', y='usuarios',
        color='plan', text='usuarios',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_plan.update_traces(textposition='outside')
    fig_plan.update_layout(xaxis_title='Plan', yaxis_title='Número de usuarios')
    return fig_plan

def distribucion_por_edad(df):
    df_edad = df[df['age_group'].notna()]
    edad_grouped = (
        df_edad.groupby('age_group')['user_id']
        .nunique().reset_index().rename(columns={'user_id': 'usuarios'})
        .sort_values(by='usuarios', ascending=False)
    )
    fig_edad = px.bar(
        edad_grouped, x='age_group', y='usuarios', color='age_group',
        labels={'age_group': 'Grupo de edad', 'usuarios': 'Usuarios'},
        color_discrete_sequence=px.colors.sequential.Sunset, text='usuarios'
    )
    return fig_edad

def mapa_usuarios_por_pais(df):
    # 1) Filtrar registros válidos con lat/lon y country_name no nulos
    df_map = df[
        df['country_name'].notna() &
        df['lat'].notna() &
        df['lon'].notna()
    ]

    # 2) Agrupar por país y coordenadas, contando usuarios únicos
    usuarios_pais_mapa = (
        df_map.groupby(['country_name', 'lat', 'lon'])['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values('usuarios', ascending=False)
    )

    # 3) Configurar capa de puntos
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=usuarios_pais_mapa,
        get_position='[lon, lat]',
        get_radius='usuarios * 70',
        get_fill_color='[0, 100, 250, 150]',
        pickable=True,
        tooltip=True,
    )

    # 4) Configurar vista inicial
    view_state = pdk.ViewState(
        latitude=usuarios_pais_mapa['lat'].mean(),
        longitude=usuarios_pais_mapa['lon'].mean(),
        zoom=2,
        pitch=0
    )

    # 5) Crear mapa
    mapa = pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{country_name}: {usuarios} usuarios"}
    )

    return mapa

def distribucion_ciudad(df):
    usuarios_por_ciudad = (
        df.groupby('city')['user_id']
        .nunique().reset_index().rename(columns={'user_id': 'usuarios'})
        .sort_values('usuarios', ascending=False)
    )
    top_ciudades = usuarios_por_ciudad.head(20)
    fig_ciudad = px.bar(
        top_ciudades, x='usuarios', y='city', orientation='h',
        color='usuarios', color_continuous_scale='Tealgrn',
        labels={'city': 'Ciudad', 'usuarios': 'Usuarios'}, text='usuarios'
    )
    return fig_ciudad

def canal(df):
    usuarios_por_canal = (
        df.groupby('channel')['user_id']
        .nunique().reset_index().rename(columns={'user_id': 'usuarios'})
        .sort_values('usuarios', ascending=False)
    )
    fig_canal = px.bar(
        usuarios_por_canal, x='channel', y='usuarios', color='usuarios',
        labels={'channel': 'Canal de adquisición', 'usuarios': 'Usuarios'},
        color_continuous_scale='burgyl', text='usuarios'
    )
    return fig_canal

def devices(df):
    usuarios_por_dispositivo = (
        df.groupby('brand_device')['user_id']
        .nunique().reset_index().rename(columns={'user_id': 'usuarios'})
        .sort_values(by='usuarios', ascending=False)
    )
    fig_devices = px.bar(
        usuarios_por_dispositivo, x='brand_device', y='usuarios',
        labels={'usuarios': 'Usuarios únicos', 'brand_device': 'Dispositivo'},
        color='usuarios', color_continuous_scale='darkmint', text='usuarios'
    )
    return fig_devices

def transacciones_por_segmento(df):
    # Agrupar por usuario único
    group_usuarios = df.groupby('user_id').agg({
        'age_group': 'first',
        'num_transactions': 'first'
    }).reset_index()

    # Agrupar por grupo de edad sumando transacciones
    transacciones_por_edad = group_usuarios.groupby('age_group')['num_transactions'].sum().reset_index()

    # Ordenar para mejor visualización
    transacciones_por_edad = transacciones_por_edad.sort_values(by='num_transactions', ascending=False)

    # Crear gráfico
    fig_txn_segmento = px.bar(
        transacciones_por_edad,
        x='age_group',
        y='num_transactions',
        labels={'age_group': 'Grupo de edad', 'num_transactions': 'Total de transacciones'},
        color='num_transactions',
        color_continuous_scale='viridis',
        text='num_transactions'
    )

    fig_txn_segmento.update_traces(textposition='outside')
    fig_txn_segmento.update_layout(
        xaxis_title='Grupo de edad',
        yaxis_title='Total de transacciones',
        title='Total de transacciones por grupo de edad'
    )

    return fig_txn_segmento

def conversion_segmento(df):
    usuarios_unicos = df.drop_duplicates(subset='user_id')
    conversion_por_plan = usuarios_unicos.groupby('plan')['converted'].agg(['count', 'sum']).reset_index()
    conversion_por_plan['conversion_rate'] = round((conversion_por_plan['sum'] / conversion_por_plan['count']) * 100, 2)
    conversion_por_plan = conversion_por_plan.sort_values(by='conversion_rate', ascending=False)
    fig_conversion_segmento = px.bar(
        conversion_por_plan, x='plan', y='conversion_rate',
        labels={'conversion_rate': '% de conversión', 'plan': 'Tipo de plan'},
        text='conversion_rate', color='conversion_rate', color_continuous_scale='gnbu'
    )
    return fig_conversion_segmento

def uso_crypto(df):
    uso_crypto = df.groupby('user_settings_crypto_unlocked')['user_id'].nunique().reset_index()
    uso_crypto.columns = ['Crypto habilitado', 'Usuarios únicos']
    uso_crypto['Crypto habilitado'] = uso_crypto['Crypto habilitado'].map({
        'True': 'Sí', 'False': 'No', True: 'Sí', False: 'No'
    })
    fig_crypto = px.pie(
        uso_crypto, values='Usuarios únicos', names='Crypto habilitado',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    return fig_crypto

def perfil_usuario(df):
    fig_plan = plan(df)
    fig_edad = distribucion_por_edad(df)
    chart = mapa_usuarios_por_pais(df)
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
            st.subheader('Usuarios por plan')
            st.plotly_chart(fig_plan, use_container_width=True)
        with col1_2:
            st.subheader('Grupo de edad')
            st.plotly_chart(fig_edad, use_container_width=True)
        with col1_3:
            st.subheader("Usuarios por país")
            st.pydeck_chart(chart, use_container_width=True)


    with col2:
        with col2_1:
            st.subheader('Top 20 ciudades con más usuarios')
            st.plotly_chart(fig_ciudad, use_container_width=True)
        with col2_2:
            st.subheader('Usuarios por canal')
            st.plotly_chart(fig_canal, use_container_width=True)
        with col2_3:
            st.subheader('Usuarios por tipo de dispositivo')
            st.plotly_chart(fig_devices, use_container_width=True)

    with col3:
        with col3_1:
            st.subheader('Transacciones por grupo de edad')
            st.plotly_chart(fig_txn_segmento, use_container_width=True)
        with col3_2:
            st.subheader('% de conversión por tipo de plan')
            st.plotly_chart(fig_conversion_segmento, use_container_width=True)
        with col3_3:
            st.subheader('Funcionalidad cripto activada')
            st.plotly_chart(fig_crypto, use_container_width=True)
