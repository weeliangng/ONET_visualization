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
                html.Label("Occupation"),
                dcc.Dropdown(id="occupation_dropdown",
                    options=dropdown_occupations(),
                    value="11-1011.00"),
                html.Div(style = {'marginBottom': 25, 'marginTop': 25}, children=[
                    html.H5("Add outward occupation graph"),
                    html.Label(children ="Related index filter for outward occupations"),
                    dcc.RangeSlider(
                            id="out_related_index_filter_slider",
                            min=1,
                            max=10,
                            step=1,
                            value=[1,5],
                            marks={i+1:str(i+1) for i in range(10)}
                    )
                ])
                ,
                html.Div(style={'marginBottom': 25, 'marginTop': 25}, children=[
                html.Label(children ="Distance"),
                    dcc.Slider(
                            id="distance_slider",
                            min=1,
                            max=10,
                            step=1,
                            value=1,
                            marks={i+1:str(i+1) for i in range(10)}
                    )
                ])
                ,
                html.Button(id="add_out_occupation_node_button", children ="Add"),
                html.Div(style={'marginBottom': 25, 'marginTop': 25}, children=[
                    html.H5("Add inward occupations to selected occupation node"),
                    html.Label(children ="Related index filter for inward occupations"),
                    dcc.RangeSlider(
                            id="in_related_index_filter_slider",
                            min=1,
                            max=10,
                            step=1,
                            value=[1,5],
                            marks={i+1:str(i+1) for i in range(10)}
                    )
                ]),
                html.Button(id="add_in_occupation_node_button", children ="Add"),
                html.Button(id="reset_graph_button", children ="Reset"),
        ])
    ]),
#############################################################
###### GRAPH
    html.Div(className="eight columns",
        children=[
            cyto.Cytoscape(
                id='network_graph',
                layout={'name': 'cose',
                    'componentSpacing': 100,
                    'nodeRepulsion': 4000},
                style={'width': '100%', 'height': '100vh'},
                boxSelectionEnabled = True,
                stylesheet= [
                    {'selector': 'node',
                    'style': {
                        'label': 'data(label)'
                    }},
                    {'selector': 'edge',
                    'style': {
                        'curve-style':'bezier',
                        'target-arrow-shape': 'vee',
                        'line-color': 'data(colour)',
                        'target-arrow-color': 'data(colour)'
                    }}

                ],
                elements=[]
#############################################################
###### Occupation details            
            )
        ]),
    html.Div(className="two columns",
        children=[
            html.H5(id="about_occupation", children = ["About Occupation"])
        ])
])

@app.callback(
    Output(component_id='network_graph', component_property='elements'),
    [Input(component_id='add_out_occupation_node_button', component_property='n_clicks'),
    Input(component_id='add_in_occupation_node_button', component_property='n_clicks')],
    [State(component_id='occupation_dropdown', component_property='value'),
    State(component_id='out_related_index_filter_slider', component_property='value'),
    State(component_id='distance_slider', component_property='value'),
    State(component_id='in_related_index_filter_slider', component_property='value'),
    State(component_id='network_graph', component_property='elements')]
)
def add_occupation(add_out_occupation_node_button, add_in_occupation_node_button, onetsoc_code, out_related_index_filter, cutoff_distance, in_related_index_filter, existing_elements):
    elements = []
    if add_out_occupation_node_button is None or add_in_occupation_node_button is None:
        return dash.no_update
    if add_out_occupation_node_button > 0:
        elements = add_elements(onetsoc_code, related_index_filter = out_related_index_filter , cutoff = cutoff_distance)
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
        add_out_occupation_node_button = 0
        add_in_occupation_node_button = 0
    if add_in_occupation_node_button > 0:
        elements = add_elements(onetsoc_code, related_index_filter = in_related_index_filter , cutoff = 1, direction ="in")
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
        add_out_occupation_node_button = 0
        add_in_occupation_node_button = 0
    return elements

@app.callback(
    [Output(component_id='add_out_occupation_node_button', component_property='n_clicks'),
    Output(component_id='add_in_occupation_node_button', component_property='n_clicks')],
    [Input(component_id='reset_graph_button', component_property='n_clicks')]
)
def reset_graph(reset_graph_button):
    return 0, 0

@app.callback(
    [Output('about_occupation', 'children'),
    Output('occupation_dropdown', 'value')],
    [Input('network_graph', 'selectedNodeData')],
    [State('occupation_dropdown', 'value')]
)
def get_selected_occupation_details(selected_node, dropdown):
    if not selected_node:
        return "",dropdown
    return selected_node[-1]['label'], selected_node[-1]['id']

def update_occupation_list(add_occupation_node,occupation_dropdown):
    
    return occupation_dropdown



def main():
    pass

if __name__ == "__main__":
    main()
    app.run_server(debug=True)