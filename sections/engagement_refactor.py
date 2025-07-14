import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import streamlit as st


# 👉 FUNCIONES AUXILIARES
# Devuelve una lista de nombres de columnas relevantes que representan el comportamiento de engagement del usuario.
# Es útil si necesitas reutilizar esta misma lista en otros lugares del código (buen patrón DRY: Don't Repeat Yourself).
def get_engagement_features():
    return [
        'num_transactions', 'total_amount_usd', 'num_transaction_types',
        'num_merchants', 'num_countries', 'pct_card_present',
        'num_notifications', 'num_contacts', 'num_successful_referrals'
    ]

def compute_engagement_score_custom(df, level_col_name='engagement_level'):
    # Obtener columnas de features
    cols_to_scale = get_engagement_features()

    # Separar X e y
    X = df[cols_to_scale]
    y = df['churned']

    # Escalar
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Modelo
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_scaled, y)

    # Calcular engagement_score_ml
    weights = model.feature_importances_ / model.feature_importances_.sum()
    df['engagement_score_ml'] = np.dot(X_scaled, weights)

    # 🔁 CAMBIO AQUÍ: calcular umbrales y categorizar manualmente
    high_threshold = df['engagement_score_ml'].quantile(0.80)
    low_threshold = df['engagement_score_ml'].quantile(0.50)

    df[level_col_name] = df['engagement_score_ml'].apply(
        lambda x: 'high' if x > high_threshold else
                  'medium' if x >= low_threshold else
                  'low'
    )

    return df


def compute_engagement_score(df, level_col_name='engagement_level'):
    # Obtener columnas de features
    cols_to_scale = get_engagement_features()

    # Separar X e y
    # X: el subconjunto de columnas del DataFrame con las features.
    # y: columna objetivo. Debe ser binaria (0 = usuario activo, 1 = churn).
    X = df[cols_to_scale]
    y = df['churned']

    # Escalar
    # Se normalizan los valores de las features a un rango entre 0 y 1, usando MinMaxScaler.
    # Esto es clave para que las variables tengan el mismo peso relativo antes de calcular el dot product.
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Modelo
    # Entrena un modelo no lineal y robusto (Gradient Boosting) para predecir el churn.
    # El random_state=42 asegura que sea reproducible.
    # Aunque no nos interesa el output de predicción en este caso, sí nos interesa la importancia de las features.
    model = GradientBoostingClassifier(random_state=42)
    model.fit(X_scaled, y)

    # Score
    # model.feature_importances_ devuelve una importancia relativa para cada feature.
    # Se normaliza (divide entre la suma) para que los pesos sumen 1.
    # Luego se aplica un dot product:
    # score = X1​⋅w1​+X2​⋅w2​+...+Xn​⋅wn​
    weights = model.feature_importances_ / model.feature_importances_.sum()
    df['engagement_score_ml'] = np.dot(X_scaled, weights)

    # Nivel
    # pd.qcut divide el score en cuantiles:
    # 0–40%: bajo
    # 40–80%: medio
    # 80–100%: alto
    # level_col_name permite que la columna resultante tenga un nombre configurable (por defecto engagement_level).
    df[level_col_name] = pd.qcut(
        df['engagement_score_ml'],
        q=[0, 0.4, 0.8, 1.0],
        labels=['low', 'medium', 'high']
    )

    return df


# 👉 FUNCIONES PRINCIPALES (NOMBRES INTACTOS)
def plot_engagement_score_chart(df):
    df = compute_engagement_score_custom(df, level_col_name='engagement_level')

    engagement_counts = (
        df['engagement_level']
        .value_counts()
        .reset_index(name='num_users')
        .rename(columns={'index': 'engagement_level'})
        .sort_values(by='engagement_level')
    )

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
    df = compute_engagement_score_custom(df, level_col_name='engagement_level')
    df['engagement_level'] = pd.Categorical(df['engagement_level'], categories=['low', 'medium', 'high'], ordered=True)

    if distribucion in df.columns:
        grouped = (
            df.groupby([distribucion, 'engagement_level'])
            .size()
            .reset_index(name='num_users')
        )

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


def promedio_usd_engagement(df):
    df = compute_engagement_score_custom(df, level_col_name='engagement_level_ml')

    df_avg = df.groupby('engagement_level_ml', as_index=False)['total_amount_usd'].mean()
    df_avg['text_usd'] = df_avg['total_amount_usd'].apply(lambda x: f"${x:,.0f}")

    fig_usd_engagement = px.bar(
        df_avg,
        x='engagement_level_ml',
        y='total_amount_usd',
        color='engagement_level_ml',
        text='text_usd',
        labels={'engagement_level_ml': 'Nivel de engagement', 'total_amount_usd': 'USD promedio'},
        color_discrete_sequence=[
            "rgb(37, 125, 152)",  # high
            "rgb(103, 219, 165)",  # medium
            "rgb(176, 242, 188)"   # low
        ]
    )

    fig_usd_engagement.update_traces(textposition='outside')
    fig_usd_engagement.update_layout(
        yaxis_title='USD promedio',
        xaxis_title='Nivel de engagement',
        yaxis_tickprefix='$',
        yaxis_tickformat=','
    )

    return fig_usd_engagement, 'Promedio transaccionado (USD) por nivel de engagement'


def engagement(df):
    fig_engagement_churn = plot_engagement_score_chart(df)
    fig_engagement_distribuciones_age_group, title_age = engagement_distribuciones(df, 'age_group')
    fig_engagement_distribuciones_plan, title_plan = engagement_distribuciones(df, 'plan')
    fig_engagement_distribuciones_channel, title_channel = engagement_distribuciones(df, 'channel')
    fig_engagement_distribuciones_country_name, title_country = engagement_distribuciones(df, 'country_name', top_n=10)
    fig_usd_engagement, title_usd = promedio_usd_engagement(df)

    col1, col2, col3 = st.columns(3)
    col1_1, col1_2 = st.columns(2)
    col2_1, col2_2 = st.columns(2)
    col3_1, col3_2 = st.columns(2)

    with col1:
        with col1_1:
            st.markdown('Distribución de Engagement Score')
            st.plotly_chart(fig_engagement_churn, use_container_width=True)
        with col1_2:
            st.markdown(title_age)
            st.plotly_chart(fig_engagement_distribuciones_age_group, use_container_width=True)
    with col2:
        with col2_1:
            st.markdown(title_plan)
            st.plotly_chart(fig_engagement_distribuciones_plan, use_container_width=True)
        with col2_2:
            st.markdown(title_channel)
            st.plotly_chart(fig_engagement_distribuciones_channel, use_container_width=True)
    with col3:
        with col3_1:
            st.markdown(title_country)
            st.plotly_chart(fig_engagement_distribuciones_country_name, use_container_width=True)
        with col3_2:
            st.markdown(title_usd)
            st.plotly_chart(fig_usd_engagement, use_container_width=True)
