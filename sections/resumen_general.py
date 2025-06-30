import streamlit as st
import pandas as pd
import plotly.express as px

from components.render_metric_card import render_metric_card

def total_users(df):
    total_users_ = df['user_id'].nunique()
    return total_users_

def conversion_rate(df):
    # % de usuarios convertidos, De cada 100 usuarios que recibieron una notificación, solo ~10 realizaron una transacción después de recibirla.

    # Positivo si es tu primer análisis, ya que hay una base de usuarios que sí responde a las notificaciones.
    # Oportunidad clara de mejora: el 90% restante no convierte, lo que puede deberse a:
    # Notificaciones mal dirigidas (segmentación pobre).
    # Contenido poco relevante o mal momento de envío.
    # Fricciones en el flujo post-notificación (clic → transacción).
    # Bajo valor percibido por el usuario.

    # ¿Qué puedes hacer con esta métrica?

    # Establecer una línea base para probar mejoras (A/B testing en canal, contenido, hora).
    # Cruzar esta tasa por canal (channel) y motivo (reason) para identificar qué tipo de notificaciones funcionan mejor.
    # Detectar segmentos que convierten mejor (edad, país, tipo de plan).

    conversion_rate_ = (
        df[df['converted']]['user_id'].nunique() / df['user_id'].nunique()
    ) * 100

    return conversion_rate_

def avg_days_to_first_txn(df):
    # Métrica 4: Promedio de días a la primera transacción (entre usuarios que transaccionaron)

    # 1) Obtener la primera transacción de cada usuario
    df_txn = df.dropna(subset=['create_date_transaction'])
    df_first_txn = df_txn.groupby('user_id')['create_date_transaction'].min().reset_index()
    df_first_txn.columns = ['user_id', 'first_transaction_date']

    # 2) Traer fecha de creación de usuario
    df_user_creation = df[['user_id', 'create_date_user']].drop_duplicates()

    # 3) Merge para calcular días a la primera transacción
    df_dias_txn = pd.merge(df_user_creation, df_first_txn, on='user_id', how='left')

    # --- ⚠️ Corregir zona horaria para evitar errores ---
    df_dias_txn['first_transaction_date'] = df_dias_txn['first_transaction_date'].dt.tz_localize(None)
    df_dias_txn['create_date_user'] = df_dias_txn['create_date_user'].dt.tz_localize(None)

    # Calcular días a la primera transacción
    df_dias_txn['dias_a_primera_txn'] = (
        df_dias_txn['first_transaction_date'] - df_dias_txn['create_date_user']
    ).dt.days

    # 4) Merge con el df principal para incorporar dias_a_primera_txn
    df = df.drop_duplicates(subset='user_id').merge(
        df_dias_txn[['user_id', 'dias_a_primera_txn']],
        on='user_id',
        how='left'
    )

    avg_days_to_first_txn_ = df['dias_a_primera_txn'].dropna().mean()

    return avg_days_to_first_txn_

def churn_rate(df):
    # Métrica 3: % de churn (usuarios activos que luego abandonaron)
    # Asegúrate de usar un df de usuarios únicos
    df_unicos = df.drop_duplicates(subset='user_id')

    total_users = df_unicos['user_id'].nunique()
    churned_users = df_unicos[(df_unicos['churned'] == True) & (df_unicos['has_transaction'] == True)]['user_id'].nunique()

    churn_rate_ = (churned_users / total_users) * 100

    return churn_rate_

def evoluacion_usuarios(df):
    # 1) Asegúrate de que las fechas de transacción están en datetime
    df['create_date_transaction'] = pd.to_datetime(df['create_date_transaction'], errors='coerce')

    # 2) Crea la columna de semana de la transacción (usando inicio de semana: lunes)
    df['semana_transaccion'] = df['create_date_transaction'].dt.to_period('W').apply(
        lambda r: r.start_time if pd.notnull(r) else pd.NaT
    )
    # 3) Usuarios activos por semana (usuarios únicos que transaccionaron)
    usuarios_activos = (
        df.dropna(subset=['semana_transaccion'])  # Asegura eliminar NaT aquí
        .groupby('semana_transaccion')['user_id']
        .nunique()
        .reset_index(name='usuarios_activos')
    )
    # 4) Usuarios nuevos por semana (basado en fecha de creación de usuario)
    df['create_date_user'] = pd.to_datetime(df['create_date_user'], errors='coerce')
    df['semana_creacion'] = df['create_date_user'].dt.to_period('W').apply(
        lambda r: r.start_time if pd.notnull(r) else pd.NaT
    )
    usuarios_nuevos = (
        df.dropna(subset=['semana_creacion'])  # Asegura eliminar NaT aquí también
        .groupby('semana_creacion')['user_id']
        .nunique()
        .reset_index(name='usuarios_nuevos')
    )
    # 5) Fusiona ambos resultados
    df_evolucion = pd.merge(
        usuarios_nuevos,
        usuarios_activos,
        left_on='semana_creacion',
        right_on='semana_transaccion',
        how='outer'
    )

    # 6) Unifica la columna de semana
    df_evolucion['semana'] = df_evolucion['semana_creacion'].combine_first(df_evolucion['semana_transaccion'])

    # 7) Elimina semanas NaT o inválidas
    df_evolucion = df_evolucion.dropna(subset=['semana']).sort_values('semana')

    # 8) Graficar con Plotly Express
    fig_evoluacion = px.line(
        df_evolucion,
        x='semana',
        y=['usuarios_nuevos', 'usuarios_activos'],
        labels={'value': 'Cantidad de usuarios', 'variable': 'Tipo de usuario', 'semana': 'Semana'},
    )
    fig_evoluacion.update_layout(xaxis=dict(tickformat='%Y-%m-%d'))  # Formato de fechas en eje X

    return fig_evoluacion

def curva_retencion(df):
    # 1) Cohorte: semana de registro
    df['cohort_week'] = df['create_date_user'].dt.to_period('W').apply(lambda r: r.start_time)
    # 2) Semana de actividad (semana de transacción)
    df['activity_week'] = df['create_date_transaction'].dt.to_period('W').apply(lambda r: r.start_time if pd.notnull(r) else pd.NaT)
    # 3) Filtrar solo usuarios con transacción
    df_active = df.dropna(subset=['activity_week'])
    # 4) Calcular semanas desde el registro correctamente
    df_active['weeks_since_signup'] = (
        (df_active['activity_week'] - df_active['cohort_week']).dt.days // 7
    )
    # 5) Usuarios únicos por cohorte y semana desde registro
    retention = (
        df_active.groupby(['cohort_week', 'weeks_since_signup'])['user_id']
        .nunique()
        .reset_index(name='active_users')
    )
    # 6) Número de usuarios en cada cohorte (tamaño base)
    cohort_sizes = (
        df.groupby('cohort_week')['user_id']
        .nunique()
        .reset_index(name='cohort_size')
    )
    # 7) Merge para calcular % de retención
    retention = retention.merge(cohort_sizes, on='cohort_week')
    retention['retention_rate'] = retention['active_users'] / retention['cohort_size']
    # 8) Pivotear para matriz de retención
    retention_matrix = retention.pivot(index='cohort_week', columns='weeks_since_signup', values='retention_rate')
    fig_matrix = px.imshow(
        retention_matrix,
        labels=dict(x='Semanas desde registro', y='Cohorte de registro', color='Tasa de retención'),
        color_continuous_scale='Agsunset'
    )
    return fig_matrix

def churned(df):
    # Agrupar usuarios únicos por estado de churn
    churn_summary = (
        df.drop_duplicates(subset='user_id')
        .groupby('churned')['user_id']
        .nunique()
        .reset_index(name='usuarios')
    )

    # Convertir True/False a etiquetas más amigables
    churn_summary['Estado'] = churn_summary['churned'].map({True: 'Churned', False: 'No Churned'})

    # Crear gráfico de pastel
    fig_churn = px.pie(
        churn_summary,
        names='Estado',
        values='usuarios',
        color='Estado',
        color_discrete_map={'Churned': '#FF6F61', 'No Churned': '#6BA292'},  # Colores personalizados
        hole=0.4  # Para hacer un donut chart
    )

    fig_churn.update_traces(textinfo='percent+label')
    
    return fig_churn

def resumen_general(df):

    total_users_ = total_users(df)
    conversion_rate_ = conversion_rate(df)
    avg_days_to_first_txn_ = avg_days_to_first_txn(df)
    churn_rate_ = churn_rate(df)
    evoluacion_usuarios_ = evoluacion_usuarios(df)
    fig_matrix = curva_retencion(df)
    fig_churn = churned(df)

    # --- MOSTRAR MÉTRICAS ---

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
