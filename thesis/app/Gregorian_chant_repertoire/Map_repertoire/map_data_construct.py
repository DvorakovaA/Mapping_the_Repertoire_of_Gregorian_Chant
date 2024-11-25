"""
File with 
* get_map_data - function get_map_data that creates data structures com_map_data and cen_map_data
which are used in javascript that creates leaflet map of communities
* get_map_of_all_data - function that returns all provences geographical data to create map of all places same way
"""

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, rgb2hex
from collections import Counter

from .models import Sources, Geography

# To change position of sources from one place
MOVES = [[0, 0.04], [0, -0.04], [-0.025, 0], [0.025, 0], [0.025, -0.04], [-0.025, 0.04], [-0.025, -0.04], [0.025, 0.04], 
         [0.012, 0.02], [0.012, -0.02], [-0.012, 0.02], [-0.012, -0.02], [0, 0.07], [0, -0.07], [0.05, 0], [-0.05, 0], 
         [0.05, 0.07], [-0.05, -0.07], [0.05, -0.07], [-0.05, 0.07]]


def get_map_data(communities: list[set [str]], edges : list [tuple]) -> dict:
    """
    Given communities of sources and info about conections beetween sources
    function constructs data structures for javascript that creates leaflet map
    map_data = {map_sources_dict : {}, no_prov_sources : [], map_com_info : {}, 
                map_cen_info : {}, edges : [], used_centuries : [], num_of_com : int, colors : []}
    """
    if communities != []: # We have data to show
        # Inicialize data structure to be returned
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
        no_prov_sources = [] # List of source_ids
        no_prov_sources_siglum = [] # source_id as well as siglum for nicer view
        used_provenances = Counter() # For position collisions
        for community in communities:
            for source in community:
                source_info = Sources.objects.filter(drupal_path = source).values()[0]
                try:
                    prov_id = source_info['provenance_id']
                    used_provenances[prov_id] = (used_provenances[prov_id] + 1) % (len(MOVES)+2)
                    place = Geography.objects.filter(provenance_id = prov_id).values()
                    lat = place[0]['latitude']
                    long = place[0]['longitude']
                    # Collisison detection
                    if used_provenances[prov_id] > 1:
                        lat += MOVES[used_provenances[prov_id]-2][0]
                        long += MOVES[used_provenances[prov_id]-2][1]
                    map_sources_dict[source] = {'siglum' : source_info['siglum'], 'provenance' : source_info['provenance'], 
                                                'title' : source_info['title'], 'century' : source_info['century'], 
                                                'cursus' : source_info['cursus'], 'lat' : lat, 'long' : long }
                    map_com_info[source] = i
                    map_cen_info[source] = source_info['num_century']
                    used_centuries.append(source_info['num_century'])
                # Source with unknown provenance
                except:
                    no_prov_sources_siglum.append({'id' : source, 'siglum' : source_info['siglum']})
                    no_prov_sources.append(source)
            i+=1
        
        used_centuries = sorted(list(set(used_centuries)))
        map_data['map_sources_dict'] = map_sources_dict
        map_data['map_com_info'] = map_com_info
        map_data['num_of_communities'] = i
        map_data['used_centuries'] = used_centuries
        map_data['map_cen_info'] = map_cen_info
        map_data['no_prov_sources'] = no_prov_sources
        map_data['no_prov_sources_siglum'] = no_prov_sources_siglum

        return map_data
    else:
        return []
    

def get_map_of_all_data_basic() -> list[list]:
    '''
    Construct data structure for js script that contains 
    geographical info about all sources with known provenances
    '''
    all_map_data = []
    unknown = 0

    sources = Sources.objects.values()
    for source in sources:
        provenance = source['provenance']
        try:
            provenance_id = source['provenance_id']
            place = Geography.objects.filter(provenance_id = provenance_id).values()
            lat = place[0]['latitude']
            long = place[0]['longitude']
            all_map_data.append([provenance, lat, long])
        except:
            unknown += 1

    return all_map_data


def get_map_of_all_data_informed() -> dict[str, list]:
    '''
    Construct data structure for js script that contains 
    info set about sources in each known provenance
    all_map_data = {'provenance_name' : [lat, long, [[url, siglum], [url, siglum], ...]], '' : [], ...}
    '''
    all_map_data = {}

    provenances = Geography.objects.values()

    for provenance in provenances:
        provenance_id = provenance['provenance_id']
        lat = provenance['latitude']
        long = provenance['longitude']
        place_sources = Sources.objects.filter(provenance_id=provenance_id).values()
        place_sources = [[source['drupal_path'], source['siglum']] for source in place_sources]
        all_map_data[provenance['provenance']] = [lat, long, place_sources]

    return all_map_data