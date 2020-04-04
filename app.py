import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from utilities import get_occupation_onetsocCode_list

def dropdown_occupations(exclude=[]):
    options = []
    for onet_occ in get_occupation_onetsocCode_list():
        for onet,occ in onet_occ.items():
            options.append({"label" : occ, "value": onet})
    return options


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)


app.layout = html.Div(children=[
    html.Div(className="two columns",
        children=[
        html.Div(children=[
                html.Label("Add Occupation"),
                dcc.Dropdown(id="occupation_dropdown",
                    options=dropdown_occupations()),
                html.Button(id="add_occupation_node", children ="Add")
        ]),

        html.Div(children=[
            html.H1(id ="occupations")

        ])
    ]),

    html.Div(className="eight columns",
        children=[
            cyto.Cytoscape(
                id='network_graph',
                layout={'name': 'cose'},
                style={'width': '100%', 'height': '100vh'},
                stylesheet= [
                    {'selector': 'node',
                    'style': {
                        'label': 'data(label)'
                    }},
                    {'selector': 'edge',
                    'style': {
                        'curve-style':'bezier',
                        'target-arrow-shape': 'vee'
                    }}

                ],
                elements=[
            {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 0, 'y': 0}},
            {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 0, 'y': 0}},
            {'data': {'source': 'one', 'target': 'two','label': 'Node 1 to 2'}},
            {'data': {'source': 'two', 'target': 'one','label': 'Node 2 to 1'}}
        ]
            )
        ])
])

@app.callback(
    Output(component_id='occupations', component_property='children'),
    [Input(component_id='add_occupation_node', component_property='n_clicks')],
    [State(component_id='occupation_dropdown', component_property='value')]
)
def update_occupation_list(add_occupation_node,occupation_dropdown):
    
    return occupation_dropdown



def main():
    pass

if __name__ == "__main__":
    main()
    app.run_server(debug=True)