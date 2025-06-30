import streamlit as st
import pandas as pd
import plotly.express as px
from components.render_metric_card import render_metric_card

def primera_transaccion(df):
    # Histograma de días a primera transacción
    # Filtrar usuarios con al menos una transacción:
    df_txn = df.dropna(subset=['create_date_transaction'])

    # Obtener la primera transacción por usuario:
    df_first_txn = df_txn.groupby('user_id')['create_date_transaction'].min().reset_index()
    df_first_txn.columns = ['user_id', 'first_transaction_date']

    # Traer fecha de registro:
    df_user_creation = df[['user_id', 'create_date_user']].drop_duplicates()
    df_merged_dias = pd.merge(df_user_creation, df_first_txn, on='user_id', how='left')

    # Asegura que ambas fechas no tengan zona horaria (tz-naive)
    df_merged_dias['first_transaction_date'] = pd.to_datetime(df_merged_dias['first_transaction_date']).dt.tz_localize(None)
    df_merged_dias['create_date_user'] = pd.to_datetime(df_merged_dias['create_date_user']).dt.tz_localize(None)

    # Calcular días a la primera transacción
    df_merged_dias['dias_a_primera_txn'] = (
        df_merged_dias['first_transaction_date'] - df_merged_dias['create_date_user']
    ).dt.days

    # Dibujar el histograma:
    fig = px.histogram(
        df_merged_dias,
        x='dias_a_primera_txn',
        nbins=300,
        labels={'dias_a_primera_txn': 'Días'},
        color_discrete_sequence=['#3BAEDA']
    )

    return fig, df_merged_dias

def usuarios_convierten_1_7_30(df_merged_dias):
    # Filtrar usuarios que sí hicieron transacción (días no nulos)
    df_convertidos = df_merged_dias.dropna(subset=['dias_a_primera_txn'])

    # Total de usuarios que convirtieron
    total_convertidos = len(df_convertidos)

    # Conversiones en 1 / 7 / 30 días
    pct_1_dia = (df_convertidos['dias_a_primera_txn'] <= 1).sum() / total_convertidos * 100
    pct_7_dias = (df_convertidos['dias_a_primera_txn'] <= 7).sum() / total_convertidos * 100
    pct_30_dias = (df_convertidos['dias_a_primera_txn'] <= 30).sum() / total_convertidos * 100

    st.markdown(render_metric_card("Conversión ≤ 1 día", f"{pct_1_dia:.1f} %"), unsafe_allow_html=True)
    st.markdown(render_metric_card("Conversión ≤ 7 días", f"{pct_7_dias:.1f} %"), unsafe_allow_html=True)
    st.markdown(render_metric_card("Conversión ≤ 30 días", f"{pct_30_dias:.1f} %"), unsafe_allow_html=True)

def nuevos_x_activos(df):
    # Agrupar usuarios nuevos por semana

    # Asegurar que la fecha está en formato datetime
    df['create_date_user'] = pd.to_datetime(df['create_date_user'])

    # Crear columna de semana de creación
    df['semana_creacion_usuario'] = df['create_date_user'].dt.to_period('W').apply(lambda r: r.start_time)

    # Agrupar por semana
    usuarios_nuevos = df.groupby('semana_creacion_usuario')['user_id'].nunique().reset_index()
    usuarios_nuevos.columns = ['semana', 'usuarios_nuevos']

    # Agrupar usuarios activos por semana

    df['create_date_transaction'] = pd.to_datetime(df['create_date_transaction'])

    # Eliminar filas con NaT en la transacción antes de crear semana
    df_filtrado = df.dropna(subset=['create_date_transaction']).copy()
    df_filtrado['semana_transaccion'] = df_filtrado['create_date_transaction'].dt.to_period('W').apply(lambda r: r.start_time)

    # Agrupar por semana, usuarios únicos que transaccionaron
    usuarios_activos = df_filtrado.groupby('semana_transaccion')['user_id'].nunique().reset_index()
    usuarios_activos.columns = ['semana', 'usuarios_activos']

    df_usuarios = pd.merge(usuarios_nuevos, usuarios_activos, on='semana', how='outer')
    df_usuarios = df_usuarios.sort_values('semana').fillna(0)

    df_usuarios_largo = df_usuarios.melt(id_vars='semana', value_vars=['usuarios_nuevos', 'usuarios_activos'],
                                     var_name='tipo_usuario', value_name='cantidad')

    # Visualización
    fig = px.line(df_usuarios_largo,
                x='semana',
                y='cantidad',
                color='tipo_usuario',
                markers=True
                )

    fig.update_layout(xaxis_title='Semana',
                    yaxis_title='Cantidad de usuarios',
                    legend_title='Tipo de usuario')
    
    return fig

def transaction_1_7_30(df):
    # 1) Calcular días hasta primera transacción
    df_merged = df.dropna(subset=['create_date_transaction']).copy()
    df_merged['create_date_transaction'] = df_merged['create_date_transaction'].dt.tz_localize(None)
    df_merged['create_date_user'] = df_merged['create_date_user'].dt.tz_localize(None)
    df_merged['dias_a_primera_txn'] = (df_merged['create_date_transaction'] - df_merged['create_date_user']).dt.days

    # 2) Quedarse solo con el primer registro de cada usuario para no duplicar conversiones
    df_first_txn = df_merged.sort_values('dias_a_primera_txn').drop_duplicates(subset='user_id', keep='first')

    # 3) Crear columnas booleanas: si convirtió en 1/7/30 días
    df_first_txn['converted_1d'] = df_first_txn['dias_a_primera_txn'] <= 1
    df_first_txn['converted_7d'] = df_first_txn['dias_a_primera_txn'] <= 7
    df_first_txn['converted_30d'] = df_first_txn['dias_a_primera_txn'] <= 30
    df_first_txn['converted_60d'] = df_first_txn['dias_a_primera_txn'] <= 60
    df_first_txn['converted_90d'] = df_first_txn['dias_a_primera_txn'] <= 90
    df_first_txn['converted_120d'] = df_first_txn['dias_a_primera_txn'] <= 120
    df_first_txn['converted_mayor_120d'] = df_first_txn['dias_a_primera_txn'] > 120

    # 4) Calcular el total de usuarios registrados
    total_users = df['user_id'].nunique()

    # 5) Calcular tasas de conversión correctamente
    conversion_1d = df_first_txn['converted_1d'].sum() / total_users * 100
    conversion_7d = df_first_txn['converted_7d'].sum() / total_users * 100
    conversion_30d = df_first_txn['converted_30d'].sum() / total_users * 100
    conversion_60d = df_first_txn['converted_60d'].sum() / total_users * 100
    conversion_90d = df_first_txn['converted_90d'].sum() / total_users * 100
    conversion_120d = df_first_txn['converted_120d'].sum() / total_users * 100
    converted_mayor_120d = df_first_txn['converted_mayor_120d'].sum() / total_users * 100

    conversion_data = {
        'Periodo': ['1 día', '7 días', '30 días', '60 días', '90 días', '120 días', 'Mayor a 120 días'],
        'Conversión (%)': [conversion_1d, conversion_7d, conversion_30d,  conversion_60d,  conversion_90d, conversion_120d, converted_mayor_120d]
    }

    fig_1_7_30 = px.bar(
        conversion_data,
        x='Periodo',
        y='Conversión (%)',
        text='Conversión (%)',
        color='Periodo',
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_1_7_30.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_1_7_30.update_layout(yaxis_range=[0, 100])

    return fig_1_7_30


def retencion_conversion(df):

    fig, df_merged_dias = primera_transaccion(df)
    fig_1_7_30 = transaction_1_7_30(df)

    col1, col2 = st.columns(2)

    with col1:
        # Histograma
        st.subheader('Días hasta la primera transacción')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # bar
        st.subheader('% de usuarios que convierten en 1, 7 y 30 días')
        fig2 = nuevos_x_activos(df)
        st.plotly_chart(fig_1_7_30, use_container_width=True)


    