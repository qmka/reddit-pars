import networkx as nx
import json

STATUS_NEW = 'new'
STATUS_COMMON = 'common'
STATUS_FAVORITE = 'favorite'


def load_graph():
    with open("graph.json", "r") as file:
        data = json.load(file)
        # создаем пустой граф
        G = nx.Graph()

        # добавляем вершины в граф
        for node in data['nodes']:
            name = node['id']
            G.add_node(name, bipartite=node['bipartite'])
            G.nodes[name]['attribute'] = node['attribute']

        # добавляем ребра в граф
        for edge in data['links']:
            G.add_edge(edge['source'], edge['target'])
    return G


def save_graph(G):
    data = nx.node_link_data(G)
    with open("graph.json", "w") as f:
        json.dump(data, f, indent=4)


def get_nodes(a, b):
    G = load_graph()
    nodes = []
    for node in G.nodes(data=True):
        if node[1]['bipartite'] == b and node[1]['attribute'] == a:
            nodes.append(node[0])
    return nodes


def get_nodes_with_bipartite(bipartite_value):
    G = load_graph()
    nodes = []
    for node in G.nodes(data=True):
        if node[1]['bipartite'] == bipartite_value:
            nodes.append(node[0])
    return nodes


def get_nodes_with_attribute(attribute_value):
    G = load_graph()
    nodes = []
    for node in G.nodes(data=True):
        if node[1]['attribute'] == attribute_value:
            nodes.append(node[0])
    return nodes


def get_name(node):
    return node[0]


def is_node_in_graph(node_name):
    G = load_graph()
    return G.has_node(node_name)
