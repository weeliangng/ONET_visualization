import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children="Hello Dash"),

    html.Div(children=[
            html.Label("Add Occupation"),
            dcc.Dropdown(id="occupation_dropdown",
                options=[
                {'label': 'New York City', 'value': 'NYC'},
                {'label': 'Montreal', 'value': 'MTL'},
                {'label': 'San Francisco', 'value': 'SF'}
                ]),
            html.Button(id="add_occupation_node", children ="Add")
    ]),

    html.Div(children=[
        html.H1(id ="occupations")

    ])


])

@app.callback(
    Output(component_id='occupations', component_property='children'),
    [Input(component_id='add_occupation_node', component_property='n_clicks')],
    [State(component_id='occupation_dropdown', component_property='value')]
)
def update_occupation_list(add_occupation_node,occupation_dropdown):
    
    return occupation_dropdown

if __name__ == "__main__":
    app.run_server(debug=True)