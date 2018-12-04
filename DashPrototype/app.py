# Imports needed to run Dash, Flask and plotly, along with pandas to read in the /csv files
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# Read in CSV file
df = pd.read_csv('./Data/Comparison.csv')

# External Stylesheet was used for this Prototype as it worked well with this layout as well as it saving time.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Declare the server type
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# This section is the beginning of the HTML section. Dash incorporates this in through Python code.
app.layout = html.Div(children=[
    html.H1(children='Wine Review Analysis'),

    html.Div(children='''
        Welcome to my Final Year Project on Wine Reviews Analysis.
    '''),
    html.Div(children='''
            The first visualisation is the actual wine prices in relation to the age and rating of a wine. Ratings in the world of wine tasters and reviews is refered to as points as you can see from below.
        '''),
    # First Visualisation Graph below.
    dcc.Graph(
        id='Real Wine Reviews',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['price'] == i]['Age'],  # This section puts the Age column as the X axis and the points column as the Y axis.
                    y=df[df['price'] == i]['points'],  # The price then shows in relation to both axis columns
                    mode='markers',
                    opacity=0.7, # Declaring opacity and marker styling parameters
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.price[:10] # This for loop will show the first 10 prices in the dataset.
            ],
            # This section is the layout for the graphs.
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'Age'},
                yaxis={'title': 'points'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ), # Below is the second graph, same information as above.
    html.Div(children='''
        The next visualisation is the corresponding KNN Predictions.
        '''),
    dcc.Graph(
        id='Predicted Wine Reviews',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['Predictions'] == i]['Age'],  # The only difference in this graph is it calls the predictive model price rather than the actual price.
                    y=df[df['Predictions'] == i]['points'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.Predictions[0:10]
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

# This call runs the server.
if __name__ == '__main__':
    app.run_server(debug=True)
