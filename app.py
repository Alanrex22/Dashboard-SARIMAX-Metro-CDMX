import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go

# Leer los datos
df = pd.read_csv("predicciones_dashboard_final.csv")

# Convertir columna 'Mes' a datetime para orden correcto
df['Mes'] = pd.to_datetime(df['Mes'], format='%Y-%m')

# Inicializar la app
app = dash.Dash(__name__)
server = app.server

# Opciones únicas
estaciones = sorted(df['estacion'].unique())
meses = sorted(df['Mes'].dt.to_period('M').astype(str).unique())

# Layout
app.layout = html.Div([
    html.H1("Dashboard de Afluencia y Delitos en el Metro CDMX", style={"textAlign": "center"}),

    html.Div([
        html.Label("Selecciona una estación:"),
        dcc.Dropdown(id='estacion-dropdown', options=[{'label': est, 'value': est} for est in estaciones], value=estaciones[0]),

        html.Label("Selecciona un mes:"),
        dcc.Dropdown(id='mes-dropdown', options=[{'label': m, 'value': m} for m in meses], value=meses[0])
    ], style={'width': '40%', 'margin': 'auto'}),

    dcc.Graph(id='grafico-evolucion')
])

# Callback
@app.callback(
    Output('grafico-evolucion', 'figure'),
    [Input('estacion-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def actualizar_grafico(estacion_seleccionada, mes_seleccionado):
    df_filtrado = df[df['estacion'] == estacion_seleccionada].sort_values('Mes')

    # Calcular crecimiento porcentual mensual de delitos
    df_filtrado['delitos_totales'] = df_filtrado['delitos_con_violencia'] + df_filtrado['delitos_sin_violencia']
    df_filtrado['variacion_delitos'] = df_filtrado['delitos_totales'].pct_change() * 100

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_filtrado['Mes'], y=df_filtrado['afluencia_predicha'],
                             mode='lines+markers', name='Afluencia Predicha', line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=df_filtrado['Mes'], y=df_filtrado['delitos_con_violencia'],
                             mode='lines+markers', name='Delitos con Violencia', line=dict(color='red')))

    fig.add_trace(go.Scatter(x=df_filtrado['Mes'], y=df_filtrado['delitos_sin_violencia'],
                             mode='lines+markers', name='Delitos sin Violencia', line=dict(color='orange')))

    fig.update_layout(title=f"Evolución en {estacion_seleccionada}",
                      xaxis_title="Mes",
                      yaxis_title="Cantidad",
                      legend_title="Indicador",
                      template="plotly_white")

    return fig

# Ejecutar
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
