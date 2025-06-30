def render_metric_card(title, value):
    return f"""
    <div class="metric-card">
        <p>{title}</p>
        <h2>{value}</h2>
    </div>
    """