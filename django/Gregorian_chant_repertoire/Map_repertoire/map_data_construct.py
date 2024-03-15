"""
Script with function that creates data structures com_map_data and cen_map_data
which are used in javascript that creates leaflet map of communities
"""

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, rgb2hex
from collections import Counter

from .models import Sources, Geography

MOVES = [[0, 0.04], [0, -0.04], [-0.025, 0], [0.025, 0], [0.025, -0.04], [-0.025, 0.04], [-0.025, -0.04], [0.025, 0.04]]
def get_map_data(communities: list[set [str]], edges : list [tuple]):
    """
    Given communities of sources and info about conections beetween sources
    function constructs data structures for javascript that creates leaflet map
    map_data = {map_sources_dict : {}, no_prov_sources : [], map_com_info : {}, map_cen_info : {}, edges : [], used_centuries : [], num_of_com : int, colors : []}
    """
    if communities != []: # We have data to show
        # Inicialize final data structure
        map_data = {'edges' : edges}

        # Color scale for points and lines connecting them 
        cmap = plt.get_cmap('plasma')
        offset = TwoSlopeNorm(vmin = 0, vcenter= (len(communities) / 2), vmax = len(communities))
        colors = []
        for b in range(len(communities)):
            scale = offset(b)
            color=rgb2hex(cmap(scale))
            colors.append(color)

        map_data['colors'] = colors
        
        # Complete info about sources and get their community and century ids
        i = 0
        map_sources_dict = {}
        map_com_info = {}
        map_cen_info = {}
        used_centuries = []
        no_prov_sources = []
        # For position collisions
        used_provenances = Counter()
        for community in communities:
            for source in community:
                source_info = Sources.objects.filter(drupal_path = source).values()[0]
                try:
                    prov_id = source_info['provenance_id']
                    used_provenances[prov_id] = (used_provenances[prov_id] + 1) % 9
                    place = Geography.objects.filter(provenance_id = prov_id).values()
                    lat = place[0]['latitude']
                    long = place[0]['longitude']
                    # Collisison detection
                    if used_provenances[prov_id] > 1:
                        lat += MOVES[used_provenances[prov_id]-2][0]
                        long += MOVES[used_provenances[prov_id]-2][1]
                    map_sources_dict[source] = {'siglum' : source_info['siglum'], 'provenance' : source_info['provenance'], 
                                                'title' : source_info['title'], 'century' : source_info['century'], 
                                                'lat' : lat, 'long' : long }
                    map_com_info[source] = i
                    map_cen_info[source] = source_info['num_century']
                    used_centuries.append(source_info['num_century'])
                except:
                    #no_prov_sources.append((source, source_info['siglum'], i))
                    no_prov_sources.append(source)
            i+=1
        
        used_centuries = sorted(list(set(used_centuries)))
        map_data['map_sources_dict'] = map_sources_dict
        map_data['map_com_info'] = map_com_info
        map_data['num_of_communities'] = i
        map_data['used_centuries'] = used_centuries
        map_data['map_cen_info'] = map_cen_info
        map_data['no_prov_sources'] = no_prov_sources

        return map_data
    else:
        return []