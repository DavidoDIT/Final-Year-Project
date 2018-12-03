import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv('./Data/Comparison.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Wine Review Analysis'),

    html.Div(children='''
        Welcome to my Final Year Project on Wine Reviews Analysis.
    '''),


    dcc.Graph(
        id='Real Wine Reviews',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['price'] == i]['Age'],
                    y=df[df['price'] == i]['points'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.price[:20]
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Age'},
                yaxis={'title': 'points'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
    dcc.Graph(
            id='Predicted Wine Reviews',
            figure={
                'data': [
                    go.Scatter(
                        x=df[df['Predictions'] == i]['Age'],
                        y=df[df['Predictions'] == i]['points'],
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}
                        },
                        name=i
                    ) for i in df.Predictions[0:20]
                ],
                'layout': go.Layout(
                    xaxis={'type': 'log', 'title': 'Age'},
                    yaxis={'title': 'points'},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
