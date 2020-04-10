import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from network_logic import *
from occupation_details import *

def dropdown_occupations(exclude=[]):
    options = []
    for onet_occ in get_occupation_onetsocCode_list():
        for onet,occ in onet_occ.items():
            options.append({"label" : occ, "value": onet})
    return options



external_stylesheets = []#'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

#nodes = [{'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 0, 'y': 0}},
#        {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 0, 'y': 0}}
#        ]
#edges = [{'data': {'source': 'one', 'target': 'two','label': 'Node 1 to 2'}},
#            {'data': {'source': 'two', 'target': 'one','label': 'Node 2 to 1'}}
#        ]
cyto.load_extra_layouts()
######### Sidebar
app.layout = html.Div(children=[
    html.Div(className="three columns",
        id = "side_bar", style={"height": "100vh", "overflow": "scroll"},
        children=default_sidebar()
        ),

#############################################################
###### GRAPH
    html.Div(className="seven columns",
        children=[
            cyto.Cytoscape(
                id='network_graph',
                layout={'name': 'cola'},
                style={'width': '100%', 'height': '100vh'},
                boxSelectionEnabled = True,
                stylesheet= [
                    {'selector': 'node',
                    'style': {
                        'label': 'data(label)',
                        'background-color': 'rgb(66, 117, 245)'
                    }},
                    {'selector': 'edge',
                    'style': {
                        'curve-style':'bezier',
                        'target-arrow-shape': 'vee',
                        'line-color': 'data(colour)',
                        'target-arrow-color': 'data(colour)'
                    }},
                    {'selector': ':selected',
                    'style': {
                        'background-color': 'rgb(166, 117, 245)'
                    }}
                ],
                elements=[]
           
            )
        ]),
#############################################################
###### Controls
    html.Div(className="two columns", 
        children=[
        html.Div(children=[
                html.Label("Layout"),
                dcc.Dropdown(id="layout_dropdown",
                    options=[
                        {'label': 'breadthfirst', 'value': 'breadthfirst'},
                        {'label': 'circle', 'value': 'circle'},
                        {'label': 'concentric', 'value': 'concentric'},
                        {'label': 'cola', 'value': 'cola'},
                        {'label': 'cose', 'value': 'cose'},
                        {'label': 'cose-bilkent', 'value': 'cose-bilkent'},
                        {'label': 'dagre', 'value': 'dagre'},
                        {'label': 'grid', 'value': 'grid'},
                        {'label': 'klay', 'value': 'klay'},
                        {'label': 'spread', 'value': 'spread'}
                    ],
                    value="cola",
                    clearable=False),
                html.Label("Occupation"),
                dcc.Dropdown(id="occupation_dropdown",
                    options=dropdown_occupations(),
                    value="11-1011.00",
                    clearable=False),
                html.Div(style = {'marginBottom': 25, 'marginTop': 25}, children=[
                    html.H5("Add outward occupation graph"),
                    html.Label(children ="Relatedness ranking filter."),
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
                    html.Label(children ="Relatedness ranking filter."),
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
                html.Hr(),
                html.Button(id="reset_graph_button", children ="Reset"),
                html.Div(children=[
                    html.P(style = {"text-align": "center"},
                        children=[
                            html.A(href="https://services.onetcenter.org/", 
                                title="This site incorporates information from O*NET Web Services. Click to learn more.",
                                children=[html.Img(src="https://www.onetcenter.org/image/link/onet-in-it.svg", 
                                        style={"width": "130px", "height": "60px", "border": "none"}, 
                                        alt="O*NET in-it"
                                            )
                                            ]
                                )
                            ]
                            ),
                    html.P(children=[
                        "This site incorporates information from ",
                        html.A(href="https://services.onetcenter.org/", children = ["O*NET Web Services"]),
                        " by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). O*NET&reg; is a trademark of USDOL/ETA."
                    ])
                ]

                )
        ])
    ]),

])

@app.callback(
    [Output(component_id='network_graph', component_property='elements'),
    Output(component_id='network_graph', component_property='layout')],
    [Input(component_id='add_out_occupation_node_button', component_property='n_clicks_timestamp'),
    Input(component_id='add_in_occupation_node_button', component_property='n_clicks_timestamp')],
    [State(component_id='layout_dropdown', component_property='value'),
    State(component_id='occupation_dropdown', component_property='value'),
    State(component_id='out_related_index_filter_slider', component_property='value'),
    State(component_id='distance_slider', component_property='value'),
    State(component_id='in_related_index_filter_slider', component_property='value'),
    State(component_id='network_graph', component_property='elements')]
)
def add_occupation(add_out_occupation_node_button, add_in_occupation_node_button, layout, onetsoc_code, out_related_index_filter, cutoff_distance, in_related_index_filter, existing_elements):
    elements = []
    if add_out_occupation_node_button is None and add_in_occupation_node_button is None:
        return elements, {'name': 'circle'}
    if add_out_occupation_node_button is None: add_out_occupation_node_button = 0
    if add_in_occupation_node_button is None: add_in_occupation_node_button = 0
    if add_out_occupation_node_button > add_in_occupation_node_button:
        elements = add_elements(onetsoc_code, related_index_filter = out_related_index_filter , cutoff = cutoff_distance)
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
    if add_in_occupation_node_button > add_out_occupation_node_button:
        elements = add_elements(onetsoc_code, related_index_filter = in_related_index_filter , cutoff = 1, direction ="in")
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
    return elements, {'name': layout}

@app.callback(
    [Output(component_id='add_out_occupation_node_button', component_property='n_clicks_timestamp'),
    Output(component_id='add_in_occupation_node_button', component_property='n_clicks_timestamp')],
    [Input(component_id='reset_graph_button', component_property='n_clicks')]
)
def reset_graph(reset_graph_button):
    if reset_graph_button is None:
        return dash.no_update, dash.no_update
    elif  reset_graph_button >0:
        add_out_occupation_node_n_clicks = None
        add_in_occupation_node_n_clicks = None
        return add_out_occupation_node_n_clicks, add_in_occupation_node_n_clicks

@app.callback(
    [Output('side_bar', 'children'),
    Output('occupation_dropdown', 'value')],
    [Input('network_graph', 'selectedNodeData')],
    [State('occupation_dropdown', 'value')]
)
def get_selected_occupation_details(selected_node, dropdown):
    if not selected_node:
        return default_sidebar(),dropdown
    return occupation_details_tab(selected_node[-1]['id']), selected_node[-1]['id']






if __name__ == "__main__":
    #main()
    app.run_server(debug=True)