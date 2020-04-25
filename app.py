import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from network_logic import *
from occupation_details import *
from skillsgap_details import *

def dropdown_occupations(exclude=[]):
    options = []
    for onet_occ in get_occupation_onetsocCode_list():
        for onet,occ in onet_occ.items():
            options.append({"label" : occ, "value": onet})
    return options

instruction_modal =  dbc.Modal(
                [
                    dbc.ModalHeader("How to interact"),
                    dbc.ModalBody(children = [
                        dcc.Markdown(
                            """
                            * Click on the occupation node to select and show occupation details
                            * Click on the edge between occupation nodes to show the gap between the two occupations
                            * Shift + drag to select multiple nodes
                            * Click and drag to move and arrange occupation nodes
                            """
                        )
                    ]),
                    dbc.ModalFooter(children = [
                            dcc.Checklist(id = "show_instruction_modal_checklist",
                                        options=[{'label': 'Do not show again', 'value': 'hideModal'}],
                                        value =[]),
                            dbc.Button(
                                "Close", id="close-centered", className="ml-auto"
                            )]
                    ),
                ],
                id="modal-centered",
                centered=True,
            )
        
            

external_stylesheets = ["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]
external_scripts = [{"src": "https://kit.fontawesome.com/ec26958d6d.js",
                    "crossorigin": "anonymous"}]


app = dash.Dash(__name__, external_stylesheets = external_stylesheets, external_scripts = external_scripts)
app.config['suppress_callback_exceptions'] = True
server = app.server

#nodes = [{'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 0, 'y': 0}},
#        {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 0, 'y': 0}}
#        ]
#edges = [{'data': {'source': 'one', 'target': 'two','label': 'Node 1 to 2'}},
#            {'data': {'source': 'two', 'target': 'one','label': 'Node 2 to 1'}}
#        ]
cyto.load_extra_layouts()

default_stylesheet = [
                    {'selector': 'node',
                    'style': {
                        'background-color': 'rgb(66, 117, 245)'
                    }},
                    {'selector': 'edge',
                    'style': {
                        'curve-style':'bezier',
                        'target-arrow-shape': 'vee',
                        'line-color': 'data(colour)',
                        'target-arrow-color': 'data(colour)'
                    }},
                    {'selector': 'node:selected',
                    'style': {
                        'label': 'data(label)',
                        'background-color': 'rgb(166, 117, 245)'
                    }}
                ]

######### Sidebar
app.layout = dbc.Row(children=[
    dbc.Col(width= 3,
        id = "side_bar", style={"height": "100vh", "overflow": "scroll"},
        children=default_sidebar()
        ),

#############################################################
###### GRAPH
    dbc.Col(width= 7,
        children=[
            cyto.Cytoscape(
                id='network_graph',
                layout={'name': 'cola'},
                style={'width': '100%', 'height': '100vh'},
                boxSelectionEnabled = True,
                stylesheet= default_stylesheet,
                elements=[]
           
            )
        ]),
#############################################################
###### Controls
    dbc.Col(width= 2, 
        children=[
        html.Div(className = "mx-3", children=[
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
                dbc.Button(id="add_out_occupation_node_button", color = "primary", outline=True, children ="Add"),
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
                dbc.Button(id="add_in_occupation_node_button", color = "primary", outline=True, children ="Add"),
                html.Hr(),
                dbc.Button(id="show_occupation_button", color = "primary", outline=True, children ="Show/hide occupation"),
                dbc.Button(id="reset_graph_button", color = "primary", outline=True, children ="Reset"),
                instruction_modal

        ])
    ]),

])

@app.callback(
    [Output(component_id='network_graph', component_property='elements'),
    Output(component_id='network_graph', component_property='layout'),
    Output(component_id='network_graph', component_property='stylesheet')],
    [Input(component_id='add_out_occupation_node_button', component_property='n_clicks_timestamp'),
    Input(component_id='add_in_occupation_node_button', component_property='n_clicks_timestamp'),
    Input(component_id='show_occupation_button', component_property='n_clicks_timestamp')],
    [State(component_id='layout_dropdown', component_property='value'),
    State(component_id='occupation_dropdown', component_property='value'),
    State(component_id='out_related_index_filter_slider', component_property='value'),
    State(component_id='distance_slider', component_property='value'),
    State(component_id='in_related_index_filter_slider', component_property='value'),
    State(component_id='show_occupation_button', component_property='n_clicks'),
    State(component_id='network_graph', component_property='elements')]
)
def add_occupation(add_out_occupation_node_button, add_in_occupation_node_button,show_occupation_button, layout, onetsoc_code, out_related_index_filter, cutoff_distance, in_related_index_filter , show_occupation_toggle, existing_elements):
    elements = []
    stylesheet = default_stylesheet
    if show_occupation_toggle is None: 
        show_occupation_button = 0
        show_occupation_toggle= 0
    if show_occupation_toggle % 2 == 0 :
        stylesheet = default_stylesheet + [{'selector': 'node',
                                                'style': {
                                                'label': 'data(label)',
                                                'background-color': 'rgb(66, 117, 245)'
                                            }},
                                             {'selector': 'node:selected',
                                                'style': {
                                                'label': 'data(label)',
                                                'background-color': 'rgb(166, 117, 245)'
                                                }}
                                            ]
    if add_out_occupation_node_button is None and add_in_occupation_node_button is None:
        return elements, {'name': 'circle'}, stylesheet
    if add_out_occupation_node_button is None: add_out_occupation_node_button = 0
    if add_in_occupation_node_button is None: add_in_occupation_node_button = 0

    buttons_click_order = sorted([add_out_occupation_node_button,add_in_occupation_node_button, show_occupation_button])

    if add_out_occupation_node_button == buttons_click_order[-1]:
        elements = add_elements(onetsoc_code, related_index_filter = out_related_index_filter , cutoff = cutoff_distance)
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
    elif add_in_occupation_node_button == buttons_click_order[-1]:
        elements = add_elements(onetsoc_code, related_index_filter = in_related_index_filter , cutoff = 1, direction ="in")
        elements = [data for data in elements if data not in existing_elements]
        elements = elements + existing_elements
    elif show_occupation_button == buttons_click_order[-1]:
        elements =  existing_elements
    return elements, {'name': layout}, stylesheet

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
    Output('occupation_dropdown', 'value'),
    Output("current_occupation_dropdown", "value"),
    Output("target_occupation_dropdown", "value"),
    Output("default_sidebar_tabs", "active_tab" )],
    [Input('network_graph', 'selectedNodeData'),
    Input('network_graph', 'selectedEdgeData')],
    [State('occupation_dropdown', 'value')]
)
def get_selected_occupation_details(selected_node , selected_edge, occupation_dropdown):
    if not selected_node and not selected_edge:
        return default_sidebar(), occupation_dropdown, None, None, None
    elif selected_node:
        return occupation_details_tab(selected_node[-1]['id']), selected_node[-1]['id'], None, None, None
    elif selected_edge:
        return default_sidebar(), occupation_dropdown, selected_edge[-1]["source"], selected_edge[-1]["target"], "tab-1"

@app.callback(
    Output('memory-skills_gap', 'data'),
    [Input("current_occupation_dropdown", "value"),
    Input("target_occupation_dropdown", "value")]
)
def perform_gap_analysis(current_occupation, target_occupation):
    if not current_occupation or not target_occupation:
        return None, None
    OnetCodeSource_reformat = remove_dash_dot(current_occupation)
    OnetCodeTarget_reformat = remove_dash_dot(target_occupation)
    skills_gap = get_skillsgap_json(OnetCodeSource_reformat, OnetCodeTarget_reformat, userId, api_key)
    return skills_gap



@app.callback(
    [Output("gap_analysis_tab", "children"),
    Output("skillsgap_details_tabs", "active_tab")],
    [Input("memory-skills_gap", "data")],
    [State("current_occupation_dropdown", "value"),
    State("target_occupation_dropdown", "value"),
    State("skillsgap_details_tabs", "active_tab")]

)
def add_skillsgap_details_tab(skills_gap, OnetCodeSource, OnetCodeTarget, active_tab):
    if not OnetCodeSource or not OnetCodeTarget:
        return skillsgap_details_tabs(), None
    if active_tab is None: 
        return skillsgap_details_tabs(), "tab-0"
    return skillsgap_details_tabs(), active_tab


@app.callback(
    Output("skillsgap_details_content","children"),
    [Input("skillsgap_details_tabs","active_tab"),
    Input("memory-skills_gap", "data"),
    Input("current_occupation_dropdown", "value"),
    Input("target_occupation_dropdown", "value")]
)
def switch_skillsgap_details_tab(active_tab, skills_gap, OnetCodeSource, OnetCodeTarget):
    #print(skills_gap)
    if not OnetCodeSource or not OnetCodeTarget or not skills_gap:
        return  None
    elif active_tab == "tab-0":
        return salary_graph(skills_gap)
    elif active_tab == "tab-1":
        return similarity_tab_details(skills_gap)
    elif active_tab == "tab-2":
        return differences_tab_details(skills_gap, OnetCodeSource, OnetCodeTarget)
    elif active_tab == "tab-3":
        return training_tab_details(skills_gap,  OnetCodeSource, OnetCodeTarget)


@app.callback(
    Output('modal-centered', 'is_open'),
    [Input('add_out_occupation_node_button', 'n_clicks'),
    Input('add_in_occupation_node_button', 'n_clicks'), 
    Input("close-centered", "n_clicks")],
    [State("show_instruction_modal_checklist", "value"),
    State("modal-centered", "is_open")]
)
def show_modal(n1, n2, n3, show_instruction_modal_checklist, is_open):
    if (n1 or n2 or n3) and len(show_instruction_modal_checklist) == 0 :
        return not is_open
    
    elif (n3) and len(show_instruction_modal_checklist) >0 and is_open == True:
        return  not is_open
    else:
        return is_open




if __name__ == "__main__":
    #main()
    app.run_server(debug=True)