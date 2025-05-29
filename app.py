import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go


# Leer los datos
df = pd.read_csv("predicciones_dashboard_final.csv")

# Convertir columna 'Mes' a datetime para orden correcto
df['Mes'] = pd.to_datetime(df['Mes'], format="%Y-%m", errors='coerce')
df = df.dropna(subset=['Mes'])  # elimina filas con fechas mal formateadas

# Inicializar la app
app = dash.Dash(__name__)
app.title = 'Dashboard Metrogit status'


# Obtener valores únicos
estaciones = sorted(df['Estacion'].unique())
meses = sorted(df['Mes'].dt.to_period('M').astype(str).unique())

# Layout de la app
app.layout = html.Div([
    html.H1("Dashboard de Afluencia y Delitos en el Metro CDMX", style={'textAlign': 'center'}),
    
    html.Label("Selecciona una estación:"),
    dcc.Dropdown(
        id='estacion_selector',
        options=[{'label': est, 'value': est} for est in estaciones],
        value=estaciones[0]
    ),

    html.Label("Selecciona un mes:"),
    dcc.Dropdown(
        id='mes_selector',
        options=[{'label': mes, 'value': mes} for mes in meses],
        value=meses[0]
    ),

    dcc.Graph(id='grafico_afluencia_delitos')
])

# Callback para actualizar gráfico
@app.callback(
    Output('grafico_afluencia_delitos', 'figure'),
    Input('estacion_selector', 'value'),
    Input('mes_selector', 'value')
)
def actualizar_grafico(estacion_seleccionada, mes_seleccionado):
    df_filtrado = df[df['Estacion'] == estacion_seleccionada]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes'], y=df_filtrado['afluencia_predicha'],
        mode='lines+markers', name='Afluencia Predicha',
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes'], y=df_filtrado['delitos_con_violencia'],
        mode='lines+markers', name='Delitos con Violencia',
        line=dict(color='red')
    ))

    fig.add_trace(go.Scatter(
        x=df_filtrado['Mes'], y=df_filtrado['delitos_sin_violencia'],
        mode='lines+markers', name='Delitos sin Violencia',
        line=dict(color='orange')
    ))

    fig.update_layout(
        title=f"Evolución en {estacion_seleccionada}",
        xaxis_title="Mes",
        yaxis_title="Cantidad",
        legend_title="Indicador",
        template="plotly_white"
    )

    return fig

# Ejecutar en Render (bind dinámico)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)

