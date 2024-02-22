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
    return len(set(a).intersection(set(b)))

def Jaccard_metrics(a : list, b : list):
    '''
    Function returns value of Jaccard metrics applied on two sets
    '''
    if len(set(a) | set(b)) != 0:
        return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))
    else:
        return 0



def get_columns(feast_ids : list[str], compare_metrics, filtering_office : list[str]):
    """
    Function that constructs lists that are
    used for listing edges of graph in desired format
    """
    drupals = Sources.objects.values_list('drupal_path')
    source_chants_dict = {}
    used_sources = []

    DO_FILTER_OFFICE = False
    if filtering_office != []:
        DO_FILTER_OFFICE = True
 
    chants_of_feasts = []
    for feast_id in feast_ids:
        chants_of_feasts += Data_Chant.objects.filter(feast_id = feast_id).values()
    for source_id in drupals:
        if DO_FILTER_OFFICE:
            print('filter')
            chants_of_source = []
            for office in filtering_office:
                chants_of_source += [chant['cantus_id'] for chant in chants_of_feasts if chant['source_id'] == source_id[0] and chant['office_id'] == office]
        else:
            chants_of_source = [chant['cantus_id'] for chant in chants_of_feasts if chant['source_id'] == source_id[0]]
        
        if chants_of_source != []:
            used_sources.append(source_id[0])
            try:
                source_chants_dict[source_id[0]].append(chants_of_source)
            except:
                source_chants_dict[source_id[0]] = chants_of_source

    used_sources = list(set(used_sources))
    print(used_sources)
    len_s = len(used_sources)
    s1_column = [j for i in [len_s * [s] for s in used_sources] for j in i]
    s2_column = len_s * used_sources

    shared_column = []
    ch1_column = []
    ch2_column = []
    for i in range(len(s1_column)):
        s1_chants = source_chants_dict[s1_column[i]]
        s2_chants = source_chants_dict[s2_column[i]]
        ch1_column.append(len(s1_chants))
        ch2_column.append(len(s2_chants))
        shared_column.append(compare_metrics(s1_chants, s2_chants))
    return s1_column, s2_column, ch1_column, ch2_column, shared_column, used_sources


def get_graph(feast_ids : list[str], filtering_office : list[str]):
    """
    Function constructs graph from networkx library
    where nodes are sources, that has chants for given feasts,
    and edges are shared chants among them
    """    
    s1_column, s2_column, ch1_column, ch2_column, shared_column, used_sources = get_columns(feast_ids, Jaccard_metrics, filtering_office)
    nodes = used_sources
    edges = [(i, j, {'weight': round(w, 2) }) for i, j, w in zip(s1_column, s2_column, shared_column) if i != j and w != 0 and (i in used_sources and j in used_sources)]
    edges_info = [(s1, s2, ch1, ch2, {'weight': round(w, 2) }) for s1, s2, ch1, ch2, w in zip(s1_column, s2_column, ch1_column, ch2_column, shared_column) if s1 != s2 and w != 0 and (s1 in used_sources and s2 in used_sources)]
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph, edges_info


def get_communities(feast_ids : list[str], filtering_office : list[str]):
    """
    Function returns communities found by Louvein algorithm and info about edges
    """
    graph, edges_info = get_graph(feast_ids, filtering_office)
    communities = nx.community.louvain_communities(graph, weight='weight')
    communities.sort(key=len, reverse=True)
    return communities, edges_info

