"""
Module providing main function get_communities
that finds communities on sources (by chants) for given feast  
"""

import networkx as nx

from .models import Data_Chant, Sources



# Metrics for measuring similarity of two sets ('chant sharingness')
def intersection_size(a : list, b : list):
    '''
    Function returns size of intersection of two sets
    '''
    return len(set(a) & set(b))

def Jaccard_metrics(a : list, b : list):
    '''
    Function returns value of Jaccard metrics applied on two sets
    '''
    if len(set(a) | set(b)) != 0:
        return len(set(a) & set(b)) / len(set(a) | set(b))
    else:
        return 0



def get_columns(feast_ids : list, compare_metrics):
    """
    Function that constructs lists that are
    used for listing edges of graph in desired format
    """
    drupals = Sources.objects.values_list('drupal_path')
    source_chants_dict = {}
    used_sources = []

    for feast_id in feast_ids:
        chants_of_feast = Data_Chant.objects.filter(feast_id = feast_id).values()
        for source_id in drupals:
            chants_of_source = [chant['cantus_id'] for chant in chants_of_feast if chant['source_id'] == source_id[0]]
            if chants_of_source != []:
                used_sources.append(source_id[0])
                try:
                    source_chants_dict[source_id[0]].append(chants_of_source)
                except:
                    source_chants_dict[source_id[0]] = chants_of_source
    
    used_sources = list(set(used_sources))
    len_s = len(used_sources)
    s1_column = [j for i in [len_s * [s] for s in used_sources] for j in i]
    s2_column = len_s * used_sources

    shared_column = []
    for i in range(len(s1_column)):
        s1_chants = source_chants_dict[s1_column[i]]
        s2_chants = source_chants_dict[s2_column[i]]
        shared_column.append(compare_metrics(s1_chants, s2_chants))

    return s1_column, s2_column, shared_column, used_sources


def get_graph(feast_ids : list[str]) -> (nx.Graph, list):
    """
    Function constructs graph from networkx library
    where nodes are sources, that has chants for given feasts,
    and edges are shared chants among them
    """    
    s1_column, s2_column, shared_column, used_sources = get_columns(feast_ids, Jaccard_metrics)
    nodes = used_sources
    edges = [(i, j, {'weight': w }) for i, j, w in zip(s1_column, s2_column, shared_column) if i != j and w != 0 and (i in used_sources and j in used_sources)]

    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph, edges


def get_communities(feast_ids : list[str]):
    """
    Function returns communities found by Louvein algorithm and info about edges
    """
    graph, edges = get_graph(feast_ids)
    communities = nx.community.louvain_communities(graph, weight='weight')
    communities.sort(key=len, reverse=True)
    return communities, edges

