import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from utils.filtrar_no_convertidos import filtrar_no_convetidos

def churned_distribucion(df, distribucion):
    # 1) Agrupar usuarios únicos por distribución y estado de churn
    churn_by_plan = (
        df.drop_duplicates(subset='user_id')
        .groupby([distribucion, 'churned'])['user_id']
        .nunique()
        .reset_index(name='usuarios')
    )

    # 2) Calcular totales por categoría para ordenar
    orden_totales = (
        churn_by_plan.groupby(distribucion)['usuarios']
        .sum()
        .sort_values(ascending=False)
        .index
    )

    # 3) Convertir columna a categórica ordenada con el orden deseado
    churn_by_plan[distribucion] = pd.Categorical(
        churn_by_plan[distribucion],
        categories=orden_totales,
        ordered=True
    )

    # 4) Mapear etiquetas legibles para churn
    churn_by_plan['Estado'] = churn_by_plan['churned'].map({True: 'Churned', False: 'No Churned'})

    # 5) Graficar barras apiladas con orden correcto y colores Set1
    fig_churn = px.bar(
        churn_by_plan.sort_values([distribucion, 'Estado']),
        x=distribucion,
        y='usuarios',
        color='Estado',
        barmode='stack',
        color_discrete_map={
            'Churned': px.colors.qualitative.Set1[0],     # rojo de Set1
            'No Churned': px.colors.qualitative.Set1[1],  # azul de Set1
        },
        text_auto=True
    )

    # 6) Configurar el eje x para que use el orden de categorías
    fig_churn.update_xaxes(categoryorder='array', categoryarray=orden_totales)
    fig_churn.update_layout(yaxis_title='Número de usuarios')

    return fig_churn, f'Distribución de churned vs. no churned ({distribucion})'


def analisis_inactividad(df, distribucion):
    # Separar usuarios activos e inactivos
    usuarios_activos = df[df['has_transaction'] == True]
    usuarios_inactivos = df[df['has_transaction'] == False]

    # Agrupar activos por canal
    activos = (
        usuarios_activos.groupby(distribucion)['user_id']
        .nunique()
        .reset_index(name='usuarios_activos')
    )

    # Agrupar inactivos por canal
    inactivos = (
        usuarios_inactivos.groupby(distribucion)['user_id']
        .nunique()
        .reset_index(name='usuarios_inactivos')
    )

    # Unir ambos
    comparacion = activos.merge(inactivos, on=distribucion, how='outer').fillna(0)

    # Calcular total y ordenar por mayor total
    comparacion['total'] = comparacion['usuarios_activos'] + comparacion['usuarios_inactivos']
    comparacion = comparacion.sort_values('total', ascending=False)

    # Graficar apilada
    fig_activos_inactivos = px.bar(
        comparacion,
        x=distribucion,
        y=['usuarios_inactivos', 'usuarios_activos'],
        barmode='stack',
        labels={'value': 'Usuarios', 'variable': 'Estado'},
        color_discrete_sequence=px.colors.qualitative.Set1,
        text_auto=True
    )

    fig_activos_inactivos.update_layout(yaxis_title='Número de usuarios')

    return fig_activos_inactivos, f'Usuarios activos vs. inactivos ({distribucion})'

def convirtieron_no_conviertieron(df, distribucion):
    # Filtrar solo usuarios notificados
    df_filtrado = df[df['has_notification'] == True].copy()

    # Agrupar por canal y estado de conversión
    df_grouped = (
        df_filtrado
        .groupby([distribucion, 'converted'])['user_id']
        .nunique()
        .reset_index()
        .pivot(index=distribucion, columns='converted', values='user_id')
        .fillna(0)
        .reset_index()
    )

    # Renombrar columnas
    df_grouped.columns = [distribucion, 'No_convirtieron', 'Convirtieron']

    # Calcular total y ordenar
    df_grouped['Total'] = df_grouped['No_convirtieron'] + df_grouped['Convirtieron']
    df_grouped = df_grouped.sort_values('Total', ascending=False)

    # Crear gráfico
    fig_convirtieron_no_convirtieron = px.bar(
        df_grouped,
        x=distribucion,
        y=['No_convirtieron', 'Convirtieron'],
        labels={'value': 'Usuarios', 'variable': 'Estado'},
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Set1,
        text_auto=True,
    )

    fig_convirtieron_no_convirtieron.update_layout(yaxis_title='Número de usuarios')

    return fig_convirtieron_no_convirtieron, f'Usuarios notificados: Convirtieron vs. No Convirtieron ({distribucion})'

def churn(df):
    
    # conviertieron
    fig_convirtieron_no_conviertieron_canal, title_channel = convirtieron_no_conviertieron(df, 'channel')
    fig_convirtieron_no_conviertieron_plan, title_plan = convirtieron_no_conviertieron(df, 'plan')
    fig_convirtieron_no_conviertieron_age_group, title_age_group = convirtieron_no_conviertieron(df, 'age_group')

    # activos inactivos
    fig_activos_inactivos_age_group, title_activos_inactivos_age_group = analisis_inactividad(df, 'age_group')
    fig_activos_inactivos_plan, title_activos_inactivos_plan= analisis_inactividad(df, 'plan')
    fig_activos_inactivos_channel, title_activos_inactivos_channel= analisis_inactividad(df, 'channel')

    # churn
    fig_churn_channel, title_churn_channel = churned_distribucion(df, 'channel')
    fig_churn_plan, title_churn_plan = churned_distribucion(df, 'plan')
    fig_churn_age_group, title_churn_age_group = churned_distribucion(df, 'age_group')

    col1, col2, col3 = st.columns(3)
    col1_1, col1_2, col1_3 = st.columns(3)
    col2_1, col2_2, col2_3 = st.columns(3)
    col3_1, col3_2, col3_3 = st.columns(3)

    with col1:
        with col1_1:
            # Pie
            st.subheader(title_channel)
            st.plotly_chart(fig_convirtieron_no_conviertieron_canal, use_container_width=True)
        with col1_2:
            # bar
            st.subheader(title_plan)
            st.plotly_chart(fig_convirtieron_no_conviertieron_plan, use_container_width=True)
        with col1_3:
            # bar
            st.subheader(title_age_group)
            st.plotly_chart(fig_convirtieron_no_conviertieron_age_group, use_container_width=True)
    with col2:
        with col2_1: 
            # Pie
            st.subheader(title_activos_inactivos_channel)
            st.plotly_chart(fig_activos_inactivos_channel, use_container_width=True)
        with col2_2: 
            # Pie
            st.subheader(title_activos_inactivos_plan)
            st.plotly_chart(fig_activos_inactivos_plan, use_container_width=True)
        with col2_3: 
            # Pie
            st.subheader(title_activos_inactivos_age_group)
            st.plotly_chart(fig_activos_inactivos_age_group, use_container_width=True)
        
    with col3:
        with col3_1: 
            # Pie
            st.subheader(title_churn_channel)
            st.plotly_chart(fig_churn_channel, use_container_width=True)
        with col3_2: 
            # Pie
            st.subheader(title_churn_plan)
            st.plotly_chart(fig_churn_plan, use_container_width=True)
        with col3_3: 
            # Pie
            st.subheader(title_churn_age_group)
            st.plotly_chart(fig_churn_age_group, use_container_width=True)
