import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from utilities import *

def dropdown_occupations(exclude=[]):
    options = []
    for onet_occ in get_occupation_onetsocCode_list():
        for onet,occ in onet_occ.items():
            options.append({"label" : occ, "value": onet})
    return options


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

nodes = [{'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 0, 'y': 0}},
         {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 0, 'y': 0}}
        ]
edges = [{'data': {'source': 'one', 'target': 'two','label': 'Node 1 to 2'}},
            {'data': {'source': 'two', 'target': 'one','label': 'Node 2 to 1'}}
        ]

app.layout = html.Div(children=[
    html.Div(className="two columns",
        children=[
        html.Div(children=[
                html.Label("Add Occupation"),
                dcc.Dropdown(id="occupation_dropdown",
                    options=dropdown_occupations(),
                    value="11-1011.00"),
                html.Button(id="add_occupation_node_button", children ="Add"),
                html.Button(id="reset_graph_button", children ="Reset"),
        ]),

        html.Div(children=[
            html.H1(id ="occupations")

        ])
    ]),

    html.Div(className="eight columns",
        children=[
            cyto.Cytoscape(
                id='network_graph',
                layout={'name': 'cose',
                    'componentSpacing': 100,
                    'nodeRepulsion': 400000,
                    'boxSelectionEnabled':True },
                style={'width': '100%', 'height': '100vh'},
                stylesheet= [
                    {'selector': 'node',
                    'style': {
                        'label': 'data(label)'
                    }},
                    {'selector': 'edge',
                    'style': {
                        'curve-style':'bezier',
                        'target-arrow-shape': 'vee',
                        'label': 'data(label)'
                    }}

                ],
                elements=[]
            
            
            )
        ]),
    html.Div(className="two columns",
        children=[
            html.H1(id="about_occupation", children = ["About Occupation"])
        ])
])

@app.callback(
    [Output(component_id='occupations', component_property='children'),
    Output(component_id='network_graph', component_property='elements')],
    [Input(component_id='add_occupation_node_button', component_property='n_clicks')],
    [State(component_id='occupation_dropdown', component_property='value'),
    State(component_id='network_graph', component_property='elements')]
)
def add_occupation(add_occupation_node_button, onetsoc_code, existing_elements):
    elements = []
    if add_occupation_node_button is None:
        return dash.no_update, dash.no_update
    if add_occupation_node_button > 0:
        elements = add_elements(onetsoc_code, related_no =3 , cutoff = 2)
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
    return onetsoc_code, elements

@app.callback(
    Output(component_id='add_occupation_node_button', component_property='n_clicks'),
    [Input(component_id='reset_graph_button', component_property='n_clicks')]
)
def reset_graph(reset_graph_button):
    return 0

@app.callback(
    Output('about_occupation', 'children'),
    [Input('network_graph', 'selectedNodeData')]
)
def get_selected_occupation_details(selected):
    if not selected:
        return
    return selected[-1]['label']

def update_occupation_list(add_occupation_node,occupation_dropdown):
    
    return occupation_dropdown



def main():
    pass

if __name__ == "__main__":
    main()
    app.run_server(debug=True)