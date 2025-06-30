def filtrar_no_convetidos(df):
    usuarios_no_convertidos = df[
        (df['has_notification'] == True) & (df['has_transaction'] == False)
    ].copy()

    return usuarios_no_convertidos