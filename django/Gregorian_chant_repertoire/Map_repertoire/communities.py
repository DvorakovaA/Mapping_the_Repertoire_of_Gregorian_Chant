"""
Module providing main function get_communities
that finds communities on sources (by chants) for given feast(s)
by given algorithm (and metric/number of topics)
"""

import networkx as nx
import numpy as np
import lzma
import pickle
import random
from itertools import combinations
from scipy.spatial.distance import jensenshannon
from sklearn.cluster import DBSCAN

from .models import Data_Chant, Sources
from django.core.files import File



# Metric for measuring similarity of two sets ('chant sharingness')
def Jaccard_metrics(a : list, b : list):
    '''
    Function returns value of Jaccard metrics applied on two sets
    '''
    if len(set(a) | set(b)) != 0:
        return len(set(a).intersection(set(b))) / len(set(a).union(set(b)))
    else:
        return 0


def find_comms_stability(community_versions : list[list[set[str]]]):
    '''
    For more versions of communities it counts Jaccard index and returns first given community
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

        if np.count_nonzero(friends_matrix) > len(source_to_id)*len(source_to_id):
            sig_level = round((np.sum(friends_matrix) / np.count_nonzero(friends_matrix)) / len(community_versions), 2)
        else:
            sig_level = 1

        return community_versions[0], float(sig_level)
    else:
        return [], 0


def get_network_info(feast_ids : list[str], compare_metrics, filtering_office : list[str], get_shared : bool):
    """
    Function that constructs data structures that are
    used by clustering algorithms and for construction of graph on map 
    based on given feast ids, metric to be used (Jaccard od ropic model comparison)
    and offices to be considered
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
            source_chants_dict[source_id[0]] = chants_of_source

    used_sources = list(set(used_sources))
    len_s = len(used_sources)
    s1_column = [j for i in [len_s * [s] for s in used_sources] for j in i]
    s2_column = len_s * used_sources

    shared_column = []
    ch1_column = []
    ch2_column = []

    if get_shared:
        if compare_metrics == 'Jaccard':
            for i in range(len(s1_column)):
                s1_chants = source_chants_dict[s1_column[i]]
                s2_chants = source_chants_dict[s2_column[i]]
                ch1_column.append(len(s1_chants))
                ch2_column.append(len(s2_chants))
                shared_column.append(Jaccard_metrics(s1_chants, s2_chants))
            edges = [(i, j, {'weight': round(w, 2) }) for i, j, w in zip(s1_column, s2_column, shared_column) if i != j and w != 0 and (i in used_sources and j in used_sources)]
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
                if np.isnan(jensenshannon(result[0], result[1])):
                    shared_column.append(0)
                else:
                    shared_column.append(jensenshannon(result[0], result[1]))
            edges = []

        # join obtained data into structure for graph and map
        edges_info = [(s1, s2, ch1, ch2, {'weight': round(w, 2) }) for s1, s2, ch1, ch2, w in zip(s1_column, s2_column, ch1_column, ch2_column, shared_column) if s1 != s2 and w != 0 and (s1 in used_sources and s2 in used_sources)]
    
    else: # We have topic model based clustering
        for i in range(len(s1_column)):
            s1_chants = source_chants_dict[s1_column[i]]
            s2_chants = source_chants_dict[s2_column[i]]
            ch1_column.append(len(s1_chants))
            ch2_column.append(len(s2_chants))
            shared_column.append('-')
        
        edges = []
        edges_info = [(s1, s2, ch1, ch2, {'weight': w}) for s1, s2, ch1, ch2, w in zip(s1_column, s2_column, ch1_column, ch2_column, shared_column) if s1 != s2 and w != 0 and (s1 in used_sources and s2 in used_sources)]
    
    return source_chants_dict, edges_info, edges, used_sources


# Louvein specific ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_graph(feast_ids : list[str], filtering_office : list[str], metric : str):
    """
    Function constructs graph from networkx library
    where nodes are sources, that has chants for given feasts,
    and edges are shared chants among them
    """
    _, edges_info, edges, used_sources = get_network_info(feast_ids=feast_ids, compare_metrics=metric, filtering_office=filtering_office, get_shared=True)
    graph = nx.Graph()
    graph.add_nodes_from(used_sources)
    graph.add_edges_from(edges)
    
    return graph, edges_info


def get_louvein_communities(feast_ids : list[str], filtering_office : list[str], add_info_algo):
    '''
    Finds communities by Louvein algorithm and returns one of them with info
    about stability and about edges for map construction
    '''
    graph, edges_info = get_graph(feast_ids=feast_ids, filtering_office=filtering_office, metric=add_info_algo)
        
    community_versions = []
    for _ in range(10):
        community_versions.append(nx.community.louvain_communities(graph, weight='weight'))
    
    communities, sig_level = find_comms_stability(community_versions)
    
    return communities, edges_info, sig_level


# DBSCAN specific ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_distance_matrix(source_chants_dict, used_sources, metric : str):
    '''
    Construct distance matrix for sources based on chants in them
    using given metric
    '''
    source_dict = {}
    i = 0
    for id in used_sources:
        source_dict[id] = i
        i += 1

    distance_matrix = np.zeros([len(used_sources), len(used_sources)])
    if metric == 'Jaccard':
        for s_i in used_sources:
            for s_j in used_sources:
                distance_matrix[source_chants_dict[s_i], source_chants_dict[s_j]] = 1 - Jaccard_metrics(source_chants_dict[s_i], source_chants_dict[s_j])
    
    else: # Comparison based on topic model
        with lzma.open('Map_repertoire/topic_models/dist_reduction.model', "rb") as model_file:
            trans = pickle.load(model_file)
            model = pickle.load(model_file)
        for s_i in used_sources:
            for s_j in used_sources:
                trans_data = trans.transform([' '.join(source_chants_dict[s_i]), ' '.join(source_chants_dict[s_j])])
                result = model.transform(trans_data)
                if np.isnan(jensenshannon(result[0], result[1])):
                    distance_matrix[source_dict[s_i], source_dict[s_j]] = 0
                else:
                    distance_matrix[source_dict[s_i], source_dict[s_j]] = jensenshannon(result[0], result[1])

    return distance_matrix, used_sources


def shuffle(perm, sources):
    shuffled_sources = [sources[j] for j in perm]
    return shuffled_sources

def unshuffle(perm, labels):
    unshuffled_labels = np.zeros(len(labels))
    for i, j in enumerate(perm):
        unshuffled_labels[j] = labels[i]
    return unshuffled_labels


def get_dbscan_communities(feast_ids : list[str], filtering_office : list[str], add_info_algo : str):
    '''
    Finds communities by DBSCAN algorithm and returns one of them with info
    about stability and about edges for map construction
    '''
    source_chants_dict, edges_info, _, used_sources = get_network_info(feast_ids=feast_ids, filtering_office=filtering_office, compare_metrics=add_info_algo, get_shared=True)

    EPS = 0.2
    MIN_SAMPLES = 3
    community_versions = []
    for _ in range(5):
        perm = list(range(len(used_sources)))
        random.shuffle(perm)
        shuff_sources = shuffle(perm, used_sources)
        distance_matrix, used_sources = get_distance_matrix(source_chants_dict, shuff_sources, add_info_algo)
        clustering = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES)
        clustering.fit(distance_matrix)
        labels = unshuffle(perm, clustering.labels_)
        groups = set(labels)
        communities_dict = {}
        for label in groups:
            communities_dict[label] = []
        for i in range(len(labels)):
            communities_dict[labels[i]].append(used_sources[i])
        community_versions.append(list(communities_dict.values()))
    
    communities, sig_level = find_comms_stability(community_versions)
    return communities, edges_info, sig_level


# Topic model specific ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_topic_model_communities(feast_ids : list[str], filtering_office : list[str], add_info_algo : str):
    ''''
    Returns communities based on how sources (=documents) are devided into topic groups
    based on chants in them and info about edges for map construction
    '''
    source_chants_dict, edges_info, _, used_sources = get_network_info(feast_ids=feast_ids, filtering_office=filtering_office, compare_metrics="", get_shared=False)

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

    # Create not lables format of data
    groups = set(labels)
    communities_dict = {}
    for label in groups:
        communities_dict[label] = []
    for i in range(len(labels)):
        communities_dict[labels[i]].append(used_sources[i])
    
    return list(communities_dict.values()), edges_info, '---'



def get_communities(feast_ids : list[str], filtering_office : list[str], algorithm : str, add_info_algo : str):
    """
    Main function of this script
    returns communities found by Louvein algorithm, DBSCAN clustering or obtained from topic models 
    and info about edges of network to be drawn on the map as well as stability measure of clusterings
    """
    if algorithm == 'Louvein':
        communities, edges_info, sig_level = get_louvein_communities(feast_ids, filtering_office, add_info_algo)
    
    elif algorithm == 'DBSCAN':
        communities, edges_info, sig_level = get_dbscan_communities(feast_ids, filtering_office, add_info_algo)

    else: #Topic models
        communities, edges_info, sig_level = get_topic_model_communities(feast_ids, filtering_office, add_info_algo)

    communities.sort(key=len, reverse=True)

    return communities, edges_info, sig_level