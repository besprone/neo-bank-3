import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import streamlit as st


def plot_engagement_score_chart(df):
    """
    Calcula y visualiza el engagement score basado en churn usando Gradient Boosting,
    usando un DataFrame que ya contiene features + columna 'churn'.
    """

    # Columnas que queremos escalar y usar como features
    cols_to_scale = [
        'num_transactions', 'total_amount_usd', 'num_transaction_types',
        'num_merchants', 'num_countries', 'pct_card_present',
        'num_notifications', 'num_contacts', 'num_successful_referrals'
    ]

    # Separar X e y
    X = df[cols_to_scale]
    y = df['churned']  # ya debe estar como 0 o 1

    # Escalar
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Entrenar modelo
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_scaled, y)

    # Importancia de variables (normalizada)
    weights = model.feature_importances_ / model.feature_importances_.sum()

    # Calcular score
    df['engagement_score_ml'] = np.dot(X_scaled, weights)

    # Categorizar score en 3 niveles
    df['engagement_level'] = pd.qcut(
        df['engagement_score_ml'],
        q=[0, 0.4, 0.8, 1.0],
        labels=['low', 'medium', 'high']
    )

    # Contar usuarios por nivel
    engagement_counts = (
        df['engagement_level']
        .value_counts()
        .reset_index(name='num_users')
        .rename(columns={'index': 'engagement_level'})
        .sort_values(by='engagement_level')
    )

    # Gráfica
    fig = px.bar(
        engagement_counts,
        x='engagement_level',
        y='num_users',
        text='num_users',
        color='engagement_level',
        color_discrete_sequence=[
                "rgb(176, 242, 188)",
                "rgb(103, 219, 165)",
                "rgb(56, 178, 163)",
                "rgb(37, 125, 152)",
            ]
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title='Nivel de Engagement',
        yaxis_title='Número de Usuarios',
        showlegend=False
    )

    return fig

def engagement_distribuciones(df, distribucion, top_n=None):

    cols_to_scale = [
        'num_transactions', 'total_amount_usd', 'num_transaction_types',
        'num_merchants', 'num_countries', 'pct_card_present',
        'num_notifications', 'num_contacts', 'num_successful_referrals'
    ]

    # Separar X e y
    X = df[cols_to_scale]
    y = df['churned']

    # Escalar
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Modelo
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_scaled, y)

    # Calcular engagement score con pesos normalizados
    weights = model.feature_importances_ / model.feature_importances_.sum()
    df['engagement_score_ml'] = np.dot(X_scaled, weights)

    # Categorizar engagement
    df['engagement_level'] = pd.qcut(
        df['engagement_score_ml'],
        q=[0, 0.4, 0.8, 1.0],
        labels=['low', 'medium', 'high']
    )
    df['engagement_level'] = pd.Categorical(
        df['engagement_level'],
        categories=['low', 'medium', 'high'],
        ordered=True
    )

    if distribucion in df.columns:
        grouped = (
            df.groupby([distribucion, 'engagement_level'])
            .size()
            .reset_index(name='num_users')
        )

        # Top N (si aplica)
        if top_n is not None:
            top_categories = (
                grouped.groupby(distribucion)['num_users']
                .sum()
                .nlargest(top_n)
                .index
                .tolist()
            )
            grouped = grouped[grouped[distribucion].isin(top_categories)]
        else:
            top_categories = (
                grouped.groupby(distribucion)['num_users']
                .sum()
                .sort_values(ascending=False)
                .index
                .tolist()
            )

        # Convertir a categoría ordenada para el eje x
        grouped[distribucion] = pd.Categorical(grouped[distribucion], categories=top_categories, ordered=True)

        fig = px.bar(
            grouped,
            x=distribucion,
            y='num_users',
            color='engagement_level',
            text='num_users',
            barmode='stack',
            category_orders={
                'engagement_level': ['low', 'medium', 'high'],
                distribucion: top_categories
            },
            color_discrete_sequence=[
                "rgb(176, 242, 188)",
                "rgb(103, 219, 165)",
                "rgb(56, 178, 163)",
            ]
        )
    else:
        counts = (
            df['engagement_level']
            .value_counts()
            .reset_index(name='num_users')
            .rename(columns={'index': 'engagement_level'})
            .sort_values(by='engagement_level')
        )

        fig = px.bar(
            counts,
            x='engagement_level',
            y='num_users',
            text='num_users',
            color='engagement_level',
            category_orders={'engagement_level': ['low', 'medium', 'high']},
            color_discrete_sequence=[
                "rgb(176, 242, 188)",
                "rgb(103, 219, 165)",
                "rgb(56, 178, 163)",
            ]
        )
        fig.update_layout(showlegend=False)

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title=distribucion if distribucion in df.columns else 'Nivel de Engagement',
        yaxis_title='Número de Usuarios'
    )

    return fig, f'Distribución de nivel de engagement por {distribucion}'




def engagement(df):
    fig_engagement_churn = plot_engagement_score_chart(df)
    fig_engagement_distribuciones_age_group, title_engagement_distribuciones_age_group = engagement_distribuciones(df, 'age_group')
    fig_engagement_distribuciones_plan, title_engagement_distribuciones_plan = engagement_distribuciones(df, 'plan')
    fig_engagement_distribuciones_channel, title_engagement_distribuciones_channel = engagement_distribuciones(df, 'channel')
    fig_engagement_distribuciones_country_name, title_engagement_distribuciones_country_name = engagement_distribuciones(df, 'country_name', top_n=10)

    col1, col2, col3 = st.columns(3)
    col1_1, col1_2 = st.columns(2)
    col2_1, col2_2 = st.columns(2)
    [col3_1] = st.columns(1)

    with col1:
        with col1_1:
            st.markdown('Distribución de Engagement Score')
            st.plotly_chart(fig_engagement_churn, use_container_width=True)
        with col1_2:
            st.markdown(title_engagement_distribuciones_age_group)
            st.plotly_chart(fig_engagement_distribuciones_age_group, use_container_width=True)
    with col2:
        with col2_1:
            st.markdown(title_engagement_distribuciones_plan)
            st.plotly_chart(fig_engagement_distribuciones_plan, use_container_width=True)
        with col2_2:
            st.markdown(title_engagement_distribuciones_channel)
            st.plotly_chart(fig_engagement_distribuciones_channel, use_container_width=True)
    with col3:
        with col3_1:
            st.markdown(title_engagement_distribuciones_country_name)
            st.plotly_chart(fig_engagement_distribuciones_country_name, use_container_width=True)
