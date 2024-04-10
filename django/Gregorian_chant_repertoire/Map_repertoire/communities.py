"""
Module providing main function get_communities
that finds communities on sources (by chants) for given feast  
"""

import networkx as nx
import numpy as np
import lzma
import pickle
from itertools import combinations
from scipy.spatial.distance import jensenshannon

from .models import Data_Chant, Sources
from django.core.files import File



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
    based on given metric (Jaccard or Topic model comparison)
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
    len_s = len(used_sources)
    s1_column = [j for i in [len_s * [s] for s in used_sources] for j in i]
    s2_column = len_s * used_sources

    shared_column = []
    ch1_column = []
    ch2_column = []

    if compare_metrics == 'Jaccard':
        for i in range(len(s1_column)):
            s1_chants = source_chants_dict[s1_column[i]]
            s2_chants = source_chants_dict[s2_column[i]]
            ch1_column.append(len(s1_chants))
            ch2_column.append(len(s2_chants))
            shared_column.append(Jaccard_metrics(s1_chants, s2_chants))
    
    else: # Comparison based on topic model
        with lzma.open('Map_repertoire/topic_models/dist_reduction.model', "rb") as model_file:
            trans = pickle.load(model_file)
            model = pickle.load(model_file)
        

        for i in range(len(s1_column)):
            s1_chants = source_chants_dict[s1_column[i]]
            s2_chants = source_chants_dict[s2_column[i]]
            ch1_column.append(len(s1_chants))
            ch2_column.append(len(s2_chants))
            trans_data = trans.transform([' '.join(s1_chants), ' '.join(s2_chants)])
            result = model.transform(trans_data)
            shared_column.append(1 - jensenshannon(result[0], result[1]))

    return s1_column, s2_column, ch1_column, ch2_column, shared_column, used_sources


def get_graph(feast_ids : list[str], filtering_office : list[str], metric : str):
    """
    Function constructs graph from networkx library
    where nodes are sources, that has chants for given feasts,
    and edges are shared chants among them
    """
    s1_column, s2_column, ch1_column, ch2_column, shared_column, used_sources = get_columns(feast_ids, metric, filtering_office)
    nodes = used_sources
    edges = [(i, j, {'weight': round(w, 2) }) for i, j, w in zip(s1_column, s2_column, shared_column) if i != j and w != 0 and (i in used_sources and j in used_sources)]
    edges_info = [(s1, s2, ch1, ch2, {'weight': round(w, 2) }) for s1, s2, ch1, ch2, w in zip(s1_column, s2_column, ch1_column, ch2_column, shared_column) if s1 != s2 and w != 0 and (s1 in used_sources and s2 in used_sources)]
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph, edges_info


def get_topic_model_communities(feast_ids : list[str], filtering_office : list[str], add_info_algo : str):
    ''''
    Returns communities based on how 
    '''
    # Get document data - sources with chants of given feats
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
            chants_of_source = []
            for office in filtering_office:
                chants_of_source += [chant['cantus_id'] for chant in chants_of_feasts if chant['source_id'] == source_id[0] and chant['office_id'] == office]
        else:
            chants_of_source = [chant['cantus_id'] for chant in chants_of_feasts if chant['source_id'] == source_id[0]]
        
        if chants_of_source != []:
            used_sources.append(source_id[0])
            #try:
            #    source_chants_dict[source_id[0]].append(chants_of_source)
            #except:
            source_chants_dict[source_id[0]] = chants_of_source

    # Get model
    if add_info_algo == '5':
        with lzma.open('Map_repertoire/topic_models/topic_5.model', "rb") as model_file:
            trans = pickle.load(model_file)
            model = pickle.load(model_file)
    elif add_info_algo == '10':
        with lzma.open('Map_repertoire/topic_models/topic_10.model', "rb") as model_file:
            trans = pickle.load(model_file)
            model = pickle.load(model_file)
    else: #20
        with lzma.open('Map_repertoire/topic_models/topic_20.model', "rb") as model_file:
            trans = pickle.load(model_file)
            model = pickle.load(model_file)
    
    trans_data = trans.transform([' '.join(s) for s in source_chants_dict.values()])
    result = model.transform(trans_data)
    labels = result.argmax(axis=1)

    groups = set(labels)
    communities_dict = {}
    for label in groups:
        communities_dict[label] = []
    for i in range(len(labels)):
        communities_dict[labels[i]].append(used_sources[i])
    
    return list(communities_dict.values()), []


def find_stable_com(community_versions : list[list[set[str]]]):
    '''
    For Louvein algorithm it gets more versions of communities and counts Jaccard index 
    (brings info anout stability of clustering)
    '''
    if community_versions != []:
        i = 0
        source_to_id = {}
        for community in community_versions[0]:
            for s in community:
                source_to_id[s] = i
                i += 1
        friends_matrix = np.zeros([len(source_to_id), len(source_to_id)])

        for com_ver in community_versions:
            for com in com_ver:
                com = sorted(list(com))
                for pair in combinations(com, 2):
                    friends_matrix[source_to_id[pair[0]], source_to_id[pair[1]]] += 1

        sig_level = round((np.sum(friends_matrix) / np.count_nonzero(friends_matrix)) / len(community_versions), 2)
        print(sig_level)
        return community_versions[0], sig_level
    else:
        return [], 0


def get_communities(feast_ids : list[str], filtering_office : list[str], algorithm : str, add_info_algo : str):
    """
    Function returns communities found by Louvein algorithm or obtained from topic models 
    and info about edges of network to be drawn on the map
    """
    if algorithm == 'Louvein':
        graph, edges_info = get_graph(feast_ids, filtering_office, add_info_algo)
        
        community_versions = []
        for _ in range(10):
            community_versions.append(nx.community.louvain_communities(graph, weight='weight'))
        
        communities, sig_level = find_stable_com(community_versions)
        communities.sort(key=len, reverse=True)
    
    else: #Topic models
        communities, edges_info = get_topic_model_communities(feast_ids, filtering_office, add_info_algo)
        communities.sort(key=len, reverse=True)
        sig_level = '---'

    return communities, edges_info, sig_level