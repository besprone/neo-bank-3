import streamlit as st
import plotly.express as px
import pydeck as pdk
import folium
from streamlit_folium import st_folium

def plan(df):

    # st.write(df)
    df_unicos = df.drop_duplicates(subset='user_id')

    df_planes = df_unicos[df_unicos['plan'].notna() & (df_unicos['plan'] != '')]
    distribucion_planes = df_planes['plan'].value_counts().reset_index()
    distribucion_planes.columns = ['plan', 'usuarios']

    fig_plan = px.bar(
        distribucion_planes, 
        x='plan', 
        y='usuarios',
        color='usuarios', 
        text='usuarios',
        color_continuous_scale='Tealgrn'
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
        edad_grouped, 
        x='age_group',
        y='usuarios', 
        color="usuarios",
        labels={'age_group': 'Grupo de edad', 'usuarios': 'Usuarios'},
        color_continuous_scale='Tealgrn'
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

    # 3) Centrar el mapa en el promedio de coordenadas
    center_lat = usuarios_pais_mapa['lat'].mean()
    center_lon = usuarios_pais_mapa['lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2, control_scale=True)

    # 4) Agregar puntos al mapa
    for _, row in usuarios_pais_mapa.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['usuarios'] ** 0.3,  # tamaño relativo
            color="#00809A",
            fill=True,
            fill_opacity=0.6,
            popup=f"{row['country_name']}: {row['usuarios']} usuarios",
            title="Usuarios por país"
        ).add_to(m)

    # 5) Mostrar el mapa en Streamlit
    st_folium(m, height=400)

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
        color_continuous_scale='Tealgrn', text='usuarios'
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
        color='usuarios', color_continuous_scale='Tealgrn', text='usuarios'
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
        color_continuous_scale='Tealgrn',
        text='num_transactions'
    )

    fig_txn_segmento.update_traces(textposition='outside')
    fig_txn_segmento.update_layout(
        xaxis_title='Grupo de edad',
        yaxis_title='Total de transacciones'
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
        text='conversion_rate', color='conversion_rate', color_continuous_scale='Tealgrn'
    )
    return fig_conversion_segmento

def uso_crypto(df):
    uso_crypto = df.groupby('user_settings_crypto_unlocked')['user_id'].nunique().reset_index()
    uso_crypto.columns = ['Crypto habilitado', 'Usuarios únicos']
    uso_crypto['Crypto habilitado'] = uso_crypto['Crypto habilitado'].map({
        'True': 'Sí', 'False': 'No', True: 'Sí', False: 'No'
    })

    fig_crypto = px.pie(
        uso_crypto,
        values='Usuarios únicos',
        names='Crypto habilitado',
        color_discrete_sequence=["rgb(37, 125, 152)", "rgb(176, 242, 188)"],  # usa Tealgrn como lista discreta
        hole=0.4
    )
    return fig_crypto

def usuarios_por_mcc(df):
    # Agrupa usuarios únicos por descripción del MCC
    usuarios_mcc = (
        df[df['mcc_description'].notna()]
        .groupby('mcc_description')['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
        .sort_values(by='usuarios', ascending=False)
    )

    # Quedarse solo con los top 20 para que la gráfica sea legible
    top_mcc = usuarios_mcc.head(20)

    fig_mcc = px.bar(
        top_mcc,
        x='usuarios',
        y='mcc_description',
        orientation='h',
        labels={'usuarios': 'Usuarios únicos', 'mcc_description': 'Categoría MCC'},
        text='usuarios',
        color='usuarios',
        color_continuous_scale='Tealgrn'
    )

    fig_mcc.update_traces(textposition='outside')
    fig_mcc.update_layout(
        xaxis_title='Número de usuarios',
        yaxis_title='Categoría MCC',
    )

    return fig_mcc

def grupo_edad_por_mcc(df):
    usuarios_mcc_age = (
        df[df['mcc_description'].notna() & df['age_group'].notna()]
        .groupby(['mcc_description', 'age_group'])['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
    )
    
    top_mccs = (
        usuarios_mcc_age.groupby('mcc_description')['usuarios']
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .index.tolist()
    )

    df_top_mcc_age = usuarios_mcc_age[usuarios_mcc_age['mcc_description'].isin(top_mccs)]

    fig_mcc_age = px.bar(
        df_top_mcc_age,
        x='mcc_description',
        y='usuarios',
        color='age_group',
        labels={
            'usuarios': 'Usuarios únicos',
            'mcc_description': 'Categoría MCC',
            'age_group': 'Grupo de edad'
        },
        text='usuarios',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_mcc_age.update_traces(textposition='inside', texttemplate='%{text}')
    fig_mcc_age.update_layout(
        xaxis_title='Categoría MCC',
        yaxis_title='Número de usuarios',
        barmode='stack',  # importante para que sea apilada
        xaxis_tickangle=-45
    )

    return fig_mcc_age

def plan_por_mcc(df):

    usuarios_mcc_plan = (
        df[df['mcc_description'].notna() & df['plan'].notna()]
        .groupby(['mcc_description', 'plan'])['user_id']
        .nunique()
        .reset_index()
        .rename(columns={'user_id': 'usuarios'})
    )

    top_mccs = (
        usuarios_mcc_plan.groupby('mcc_description')['usuarios']
        .sum()
        .sort_values(ascending=False)
        .head(20)
        .index.tolist()
    )

    df_top_mcc_plan = usuarios_mcc_plan[usuarios_mcc_plan['mcc_description'].isin(top_mccs)]
    
    fig_mcc_plan = px.bar(
        df_top_mcc_plan,
        x='mcc_description',
        y='usuarios',
        color='plan',
        labels={
            'usuarios': 'Usuarios únicos',
            'mcc_description': 'Categoría MCC',
            'plan': 'Plan'
        },
        text='usuarios',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_mcc_plan.update_traces(textposition='inside', texttemplate='%{text}')
    fig_mcc_plan.update_layout(
        xaxis_title='Categoría MCC',
        yaxis_title='Número de usuarios',
        barmode='stack',
        xaxis_tickangle=-45
    )

    return fig_mcc_plan

def perfil_usuario(df):
    fig_plan = plan(df)
    fig_edad = distribucion_por_edad(df)
    # chart = mapa_usuarios_por_pais(df)
    fig_ciudad = distribucion_ciudad(df)
    fig_canal = canal(df)
    fig_devices = devices(df)
    fig_txn_segmento = transacciones_por_segmento(df)
    fig_conversion_segmento = conversion_segmento(df)
    fig_crypto = uso_crypto(df)
    fig_mcc = usuarios_por_mcc(df)
    fig_mcc_age = grupo_edad_por_mcc(df)
    fig_mcc_plan = plan_por_mcc(df)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1_1, col1_2, col1_3 = st.columns(3)
    col2_1, col2_2, col2_3 = st.columns(3)
    col3_1, col3_2, col3_3 = st.columns(3)
    [col4_1] = st.columns(1)
    [col5_1] = st.columns(1)
    [col6_1] = st.columns(1)

    with col1:
        with col1_1:
            st.markdown('Usuarios por plan')
            st.plotly_chart(fig_plan, use_container_width=True)
        with col1_2:
            st.markdown('Grupo de edad')
            st.plotly_chart(fig_edad, use_container_width=True)
        with col1_3:
            st.markdown("Usuarios por país")
            mapa_usuarios_por_pais(df)


    with col2:
        with col2_1:
            st.markdown('Top 20 ciudades con más usuarios')
            st.plotly_chart(fig_ciudad, use_container_width=True)
        with col2_2:
            st.markdown('Usuarios por canal')
            st.plotly_chart(fig_canal, use_container_width=True)
        with col2_3:
            st.markdown('Usuarios por tipo de dispositivo')
            st.plotly_chart(fig_devices, use_container_width=True)

    with col3:
        with col3_1:
            st.markdown('Transacciones por grupo de edad')
            st.plotly_chart(fig_txn_segmento, use_container_width=True)
        with col3_2:
            st.markdown('% de conversión por tipo de plan')
            st.plotly_chart(fig_conversion_segmento, use_container_width=True)
        with col3_3:
            st.markdown('Funcionalidad cripto activada')
            st.plotly_chart(fig_crypto, use_container_width=True)

    with col4:
        with col4_1:
            st.markdown('Usuarios por Categoría MCC')
            st.plotly_chart(fig_mcc, use_container_width=True)
    with col5:
        with col5_1:
            st.markdown('Categoría MCC por grupo de edad')
            st.plotly_chart(fig_mcc_age, use_container_width=True)
    with col6:
        with col6_1:
            st.markdown('Categoría MCC por plan')
            st.plotly_chart(fig_mcc_plan, use_container_width=True)
        
