"""
Module providing main function get_communities
that finds communities on sources (by chants) for given feast  
"""

import networkx as nx
from .models import Data_Chant


# Metrics for measuring similarity of two sets ('chant sharingness')
def intersection_size(a, b):
    return len(set(a) & set(b))

def Jaccard_metrics(a, b):
    if len(set(a) | set(b)) != 0:
        return len(set(a) & set(b)) / len(set(a) | set(b))
    else:
        return 0


def get_columns(chants : list):
    """
    """
    pass


def get_graph(feast_ids : list [str]):
    """
    Function constructs graph from networkx library
    where nodes are sources, that has chants for given feast(s),
    and edges are shared chants among them
    """

    chants = []
    for feast_id in feast_ids:
        chants += Data_Chant.objects.filter(feast_id = feast_id).values()

    s1_column, s2_column, shared_column = get_columns(chants)
    nodes = set([chant['source_id'] for chant in chants])
    edges = [(i, j, {'weight': w }) for i, j, w in zip(s1_column, s2_column, shared_column) if i != j and w != 0]
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph


def get_communities(feast_ids : list [str]) -> list [set [str]]:
    """
    Function returns communities found by Louvein algorithm
    """
    graph = get_graph(feast_ids)
    communities = nx.community.louvain_communities(graph, weight='weight')

    return communities

