import streamlit as st
import pandas as pd
import plotly.express as px

from components.render_metric_card import render_metric_card

def total_users(df):
    return df['user_id'].nunique()

def conversion_rate(df):
    conversion_rate_ = (
        df[df['converted'] == True]['user_id'].nunique() / df['user_id'].nunique()
    ) * 100
    return conversion_rate_

def avg_days_to_first_txn(df):
    avg_days_to_first_txn_ = df['dias_a_primera_txn'].dropna().mean()
    return avg_days_to_first_txn_

def churn_rate(df):
    total_users = df['user_id'].nunique()
    churned_users = df[(df['churned'] == True) & (df['has_transaction'] == True)]['user_id'].nunique()
    churn_rate_ = (churned_users / total_users) * 100
    return churn_rate_

def evoluacion_usuarios(df):
    # Calcular usuarios activos por semana
    df['create_date_transaction'] = pd.to_datetime(df['first_transaction_date'], errors='coerce')
    df['semana_transaccion'] = df['create_date_transaction'].dt.to_period('W').apply(
        lambda r: r.start_time if pd.notnull(r) else pd.NaT
    )
    usuarios_activos = (
        df.dropna(subset=['semana_transaccion'])
        .groupby('semana_transaccion')['user_id']
        .nunique()
        .reset_index(name='usuarios_activos')
    )

    # Calcular usuarios nuevos por semana
    df['create_date_user'] = pd.to_datetime(df['create_date_user'], errors='coerce')
    df['semana_creacion'] = df['create_date_user'].dt.to_period('W').apply(
        lambda r: r.start_time if pd.notnull(r) else pd.NaT
    )
    usuarios_nuevos = (
        df.dropna(subset=['semana_creacion'])
        .groupby('semana_creacion')['user_id']
        .nunique()
        .reset_index(name='usuarios_nuevos')
    )

    df_evolucion = pd.merge(
        usuarios_nuevos,
        usuarios_activos,
        left_on='semana_creacion',
        right_on='semana_transaccion',
        how='outer'
    )
    df_evolucion['semana'] = df_evolucion['semana_creacion'].combine_first(df_evolucion['semana_transaccion'])
    df_evolucion = df_evolucion.dropna(subset=['semana']).sort_values('semana')

    fig_evoluacion = px.line(
        df_evolucion,
        x='semana',
        y=['usuarios_nuevos', 'usuarios_activos'],
        labels={'value': 'Cantidad de usuarios', 'variable': 'Tipo de usuario', 'semana': 'Semana'},
    )
    fig_evoluacion.update_layout(xaxis=dict(tickformat='%Y-%m-%d'))
    return fig_evoluacion

def curva_retencion(df_retencion_cohortes):
    # Pivot para matriz de retención
    retention_pivot = df_retencion_cohortes.pivot(
        index='cohort_week',
        columns='weeks_since_signup',
        values='active_users'
    ).fillna(0)

    # Normalizar: tasa de retención por cohorte
    retention_rate = retention_pivot.divide(retention_pivot.iloc[:, 0], axis=0)

    # Plot
    fig_matrix = px.imshow(
        retention_rate,
        labels=dict(x='Semanas desde registro', y='Cohorte de registro', color='Tasa de retención'),
        color_continuous_scale='Agsunset'
    )
    return fig_matrix

def churned(df):
    churn_summary = (
        df.drop_duplicates(subset='user_id')
        .groupby('churned')['user_id']
        .nunique()
        .reset_index(name='usuarios')
    )
    churn_summary['Estado'] = churn_summary['churned'].map({True: 'Churned', False: 'No Churned'})
    fig_churn = px.pie(
        churn_summary,
        names='Estado',
        values='usuarios',
        color='Estado',
        color_discrete_map={'Churned': '#FF6F61', 'No Churned': '#6BA292'},
        hole=0.4
    )
    fig_churn.update_traces(textinfo='percent+label')
    return fig_churn

def resumen_general(df, df_retencion_cohortes):
    total_users_ = total_users(df)
    conversion_rate_ = conversion_rate(df)
    avg_days_to_first_txn_ = avg_days_to_first_txn(df)
    churn_rate_ = churn_rate(df)
    evoluacion_usuarios_ = evoluacion_usuarios(df)
    fig_matrix = curva_retencion(df_retencion_cohortes)
    fig_churn = churned(df)

    col1, col2 = st.columns(2)
    col1_1, col1_2, col1_3, col1_4 = st.columns(4)
    col2_1, col2_2, col2_3 = st.columns(3)

    with col1:
        with col1_1:
            st.markdown(render_metric_card("Total de usuarios", f"{total_users_:,}"), unsafe_allow_html=True)
        with col1_2:
            st.markdown(render_metric_card("% de conversión", f"{conversion_rate_:.2f}%"), unsafe_allow_html=True)
        with col1_3:
            st.markdown(render_metric_card("AVG de días a la primera transacción", f"{avg_days_to_first_txn_:.2f} días"), unsafe_allow_html=True)
        with col1_4:
            st.markdown(render_metric_card("% de churn", f"{churn_rate_:.2f}%"), unsafe_allow_html=True)

    with col2:
        with col2_1:
            st.subheader('Evolución semanal de usuarios nuevos vs. activos')
            st.plotly_chart(evoluacion_usuarios_, use_container_width=True)
        with col2_2:
            st.subheader('Curva de retención por cohortes semanales')
            st.plotly_chart(fig_matrix, use_container_width=True)
        with col2_3:
            st.subheader('Usuarios churned vs. no churned')
            st.plotly_chart(fig_churn, use_container_width=True)
