import dash
import networkx as nx
import sqlite3

import dash
import dash_cytoscape as cyto
import dash_html_components as html

#

def get_relevant_edges(id,  data, max_index = 10):
    nodes = list()
    edges = list()
    nodes.append(id)
    for node in nodes: 
        #print(len(nodes))
        edges_with_node = list(filter(lambda edge: edge["source"]==node and int(edge["related_index"])<=max_index, data))
        edges += edges_with_node
        for edge in edges_with_node:
            if edge["target"] not in nodes:
                nodes.append(edge["target"])
        

    return edges

def get_career_changers_matrix():
    conn = sqlite3.connect('./data/ONET.sqlite')
    career_changer_sql = "select * from career_changers_matrix"
    c = conn.cursor()
    data = []
    for row in c.execute(career_changer_sql):
        data.append({
            "source": row[0],
            "target": row[1],
            "related_index": row[2]
        })
    conn.close()
    return data

def get_occupation_data():
    conn = sqlite3.connect('./data/ONET.sqlite')
    occupation_data_sql = "select * from occupation_data"
    c = conn.cursor()
    occupation_data_dictionary = dict()
    for row in c.execute(occupation_data_sql):
        occupation_data_dictionary[row[0]] = {
            "id": row[0],
            "occupation": row[1],
            "occupation_description": row[2]
        }
    conn.close()
    return occupation_data_dictionary

def create_network(data):
    G=nx.DiGraph()
    occupation_data_dict = get_occupation_data()
    for edge in data:
        G.add_node(edge["target"], label = occupation_data_dict[edge["target"]]["occupation"])
        G.add_node(edge["source"], label = occupation_data_dict[edge["source"]]["occupation"])
        G.add_edge(edge["source"], edge["target"], related_index = edge["related_index"])
    return G

def shorten_network(source_node, G, cutoff = 5):
    pl = nx.single_source_shortest_path_length(G, source = source_node, cutoff = cutoff)
    #p = nx.single_source_shortest_path(G, source = source_node, cutoff = cutoff)
    nodes_to_remove = set(G.nodes()).difference(set(pl.keys()))
    for node in nodes_to_remove:
        G.remove_node(node)
    return G
def create_graph(G):
    cytoscape_data_format = nx.cytoscape_data(G)
    nodes = cytoscape_data_format["elements"]["nodes"] 
    edges = cytoscape_data_format["elements"]["edges"]

    app = dash.Dash(__name__)

    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'breadthfirst'},
            style={'width': '100%', 'height': '1400px'},
            elements= nodes + edges
        )
    ])

    app.run_server(debug=True)

#app.run_server(debug=True)


def main():
    starting_node = '11-1011.00'
    career_changers_data = get_career_changers_matrix()
    relevant_edges = get_relevant_edges(starting_node, career_changers_data,2)
    graph = create_network(relevant_edges)
    graph = shorten_network(starting_node, graph, cutoff = 20)
    
    create_graph(graph)
    

if __name__ == '__main__':
    main()
    