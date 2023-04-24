import networkx as nx
import json

STATUS_NEW = 'new'
STATUS_COMMON = 'common'
STATUS_FAVORITE = 'favorite'


def load_graph():
    with open("graph.json", "r") as file:
        data = json.load(file)
        G = nx.Graph()

        for node in data['nodes']:
            name = node['id']
            G.add_node(name, bipartite=node['bipartite'])
            G.nodes[name]['attribute'] = node['attribute']

        for edge in data['links']:
            G.add_edge(edge['source'], edge['target'])
    return G


def save_graph(G):
    data = nx.node_link_data(G)
    with open("graph.json", "w") as f:
        json.dump(data, f, indent=4)


def get_nodes(attribute=None, bipartite=None):
    G = load_graph()
    nodes = []
    for node in G.nodes(data=True):
        if not filter_node(node, attribute, bipartite):
            continue
        nodes.append(node[0])
    return nodes


def filter_node(node, attribute, bipartite):
    a_match = attribute is None or node[1]['attribute'] == attribute
    b_match = bipartite is None or node[1]['bipartite'] == bipartite
    return a_match and b_match


def get_name(node):
    return node[0]


def is_node_in_graph(node_name):
    G = load_graph()
    return G.has_node(node_name)
