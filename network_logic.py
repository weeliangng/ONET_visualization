import sqlite3
import dash_cytoscape as cyto
import networkx as nx
import matplotlib.cm as cm
import numpy as np

#################################################################################
# DB related functions
def get_occupation_onetsocCode_list():
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_sql = """select distinct career_changers_matrix.onetsoc_code, title as occupation from career_changers_matrix 
                            inner join occupation_data on career_changers_matrix.onetsoc_code = occupation_data.onetsoc_code;"""
    c = conn.cursor()
    data = []
    for row in c.execute(onetsoc_occupation_sql):
        data.append({
            row[0]: row[1]
        })
    conn.close()
    return data

def get_occupation_onetsocCode_dict():
    conn = sqlite3.connect('./data/ONET.sqlite')
    onetsoc_occupation_sql = """select distinct career_changers_matrix.onetsoc_code, title as occupation from career_changers_matrix 
                            inner join occupation_data on career_changers_matrix.onetsoc_code = occupation_data.onetsoc_code;"""
    c = conn.cursor()

    occupation_onetsocCode_dict = dict()
    for row in c.execute(onetsoc_occupation_sql):
        occupation_onetsocCode_dict[row[0]] =  row[1]
    return occupation_onetsocCode_dict

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
#################################################################################

def get_relevant_edges(id,  data, filter_index = [0, 10], direction = "out"):
    nodes = list()
    edges = list()
    nodes.append(id)
    for node in nodes: 
        #print(len(nodes))
        if direction == "out":
            edges_with_node = list(filter(lambda edge: edge["source"]==node and int(edge["related_index"])<=int(filter_index[1]) and int(edge["related_index"])>=int(filter_index[0]), data))
        elif direction == "in":
            edges_with_node = list(filter(lambda edge: edge["target"]==node and int(edge["related_index"])<=int(filter_index[1]) and int(edge["related_index"])>=int(filter_index[0]), data))
        edges += edges_with_node
        for edge in edges_with_node:
            if direction == "out":
                if edge["target"] not in nodes:
                    nodes.append(edge["target"])
            elif direction == "in":
                if edge["source"] not in nodes:
                    nodes.append(edge["source"])
    return edges

def create_network(data):
    G=nx.DiGraph()
    occupation_data_dict = get_occupation_data()
    rgb_colour = get_colour()
    for edge in data:
        G.add_node(edge["target"], label = occupation_data_dict[edge["target"]]["occupation"])
        G.add_node(edge["source"], label = occupation_data_dict[edge["source"]]["occupation"])
        G.add_edge(edge["source"], edge["target"], related_index = edge["related_index"], id = edge["source"] + "->" +edge["target"], label = edge["related_index"], colour = rgb_colour[edge["related_index"]])
    #print(G.edges.data())
    return G

def shorten_network(source_node, G, cutoff = 5, direction = "out"):
    if direction == "out":
        pl = nx.single_source_shortest_path_length(G, source = source_node, cutoff = cutoff)
    elif direction == "in":
        pl = nx.shortest_path_length(G, target = source_node)
        pl = { node: path_length for node, path_length in pl.items() if path_length <= cutoff}
    #p = nx.single_source_shortest_path(G, source = source_node, cutoff = cutoff)
    nodes_to_remove = set(G.nodes()).difference(set(pl.keys()))
    for node in nodes_to_remove:
        G.remove_node(node)
    return G

def create_elements_from_graph(G):
    cytoscape_data_format = nx.cytoscape_data(G)
    nodes = cytoscape_data_format["elements"]["nodes"] 
    edges = cytoscape_data_format["elements"]["edges"]
    elements= nodes + edges

    return elements

def add_elements(onetsoc_code, related_index_filter, cutoff, direction = "out"):
    career_changers_data = get_career_changers_matrix()
    relevant_edges = get_relevant_edges(onetsoc_code, career_changers_data, related_index_filter, direction)
    graph = create_network(relevant_edges)
    graph = shorten_network(onetsoc_code, graph, cutoff, direction)
    elements =create_elements_from_graph(graph)
    return elements

def get_colour():
    colour_dict = dict()
    num_range = np.linspace(256, 1,10)
    index = 1
    for num in num_range:
        colour = cm.Blues(int(num))
        rgb_colour = "rgb({},{},{})".format(int(colour[0]*255) , int(colour[1]*255) , int(colour[2]*255))
        colour_dict[index] = rgb_colour
        index +=1
    return colour_dict