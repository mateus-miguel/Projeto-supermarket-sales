import dash
from dash import html, dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

import plotly.express as px
import dash_bootstrap_components as dbc


app = dash.Dash(__name__)
server = app.server

# ------------- Data -------------
df = pd.read_csv('supermarket_sales.csv', sep=',')
df['Date'] = pd.to_datetime(df['Date'])

variable_dict = {
    'gross income': 'Renda Bruta',
    'Rating': 'Avaliação Média'
}


# ------------- Layout -------------
app.layout = html.Div(children=[
    html.H5('Cidades:'),
    dcc.Checklist(
        id='checklist-cities',
        options=[{'label': i, 'value':i} for i in df['City'].unique()],
        value=[i for i in df['City'].unique()]
    ),
    html.H5('Variável de análise:'),
    dcc.RadioItems(
        id='radio-variable',
        options=[
            {'label': 'Renda Bruta', 'value': 'gross income'},
            {'label': 'Avaliação', 'value': 'Rating'}
        ],
        value='gross income'
    ),
    dcc.Graph(id='gross-income-graph'),
    dcc.Graph(id='payment-graph'),
    dcc.Graph(id='product-line-graph')
])


# ------------- Callbacks -------------
@app.callback(
    [
        Output('gross-income-graph', 'figure'),
        Output('payment-graph', 'figure'),
        Output('product-line-graph', 'figure')
    ],
    [
        Input(component_id='checklist-cities', component_property='value'),
        Input(component_id='radio-variable', component_property='value')
    ]
)
def update_figures(cities, variable):
    # cities = ('Yangon', 'Mandalay')
    # variable = 'Rating'
    operation = np.sum if variable == 'gross income' else np.mean

    # Gross income graph
    df_filtered = df[df['City'].isin(cities)] # Filter by tuple of cities
    df_city = df_filtered.groupby('City')[variable].apply(operation).to_frame()
    fig1 = px.histogram(df_city, x=df_city.index, y=df_city[variable])
    fig1.update_traces(marker_line_width=1, marker_line_color='black')
    fig1.update_layout(height=300, xaxis_title='Cidades', yaxis_title=variable_dict[variable])

    # Payment graph
    df_payment = df_filtered.groupby('Payment')[variable].apply(operation).to_frame()
    fig2 = px.histogram(df_payment, x=df_payment[variable], y=df_payment.index)
    fig2.update_traces(marker_line_width=1, marker_line_color='black')
    fig2.update_layout(height=300, xaxis_title=variable_dict[variable], yaxis_title='Pagamento')

    # Product line graph
    df_products = df_filtered.groupby(['City', 'Product line'])[variable].apply(operation).to_frame().reset_index()
    fig3 = px.histogram(df_products, x=df_products[variable], y=df_products['Product line'], color=df_products['City'], barmode='group')
    fig3.update_traces(marker_line_width=1, marker_line_color='black')
    fig3.update_layout(height=300, xaxis_title=variable_dict[variable], yaxis_title='Linhas de Produtos')

    return fig1, fig2, fig3


# ------------- Run server -------------
if __name__ == '__main__':
    app.run_server(debug=False)