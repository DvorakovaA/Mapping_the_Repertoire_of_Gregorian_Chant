"""
Module providing main function get_map
that returns html of folium map visualization of given sources communities
"""

import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, rgb2hex

from .models import Sources, Geography

map_centre = [47.466667, 11.166667] # Centre of returned maps


def get_map(communities : list [set [str]]):
    map = folium.Map(map_centre, zoom_start=5, height='70%', width='70%', tiles=None)

    # Color scale for points amd lines connecting them 
    cmap = plt.get_cmap('plasma')
    offset = TwoSlopeNorm(vmin = 0, vcenter= (len(communities) / 2), vmax = len(communities))
    colors = []
    for b in range(len(communities)):
        scale = offset(b)
        color=rgb2hex(cmap(scale))
        colors.append(color)
    
    # Get dict of sources in communities
    sources_dict = {}
    i = 0
    for community in communities:
        for source in community:
            sources_dict[source] = i
            i += 1

    used_sources = [Sources.objects.filter(drupal_path = source).values()[0] for source in sources_dict.keys()]
    num_centuries = [s['num_century'] for s in used_sources]
    provenance_ids = [s['provenance_id'] for s in used_sources]
    centuries = [s['century'] for s in used_sources]
    sizes = ...
    siglums = ...

    # Layers
    century_layers = {}
    for century in num_centuries:
        c_layer = folium.FeatureGroup(name=str(century) + ". century", show=False)
        century_layers[century] = c_layer
        map.add_child(c_layer)

    community_layers = {}

    # Points
    i, j = 0, 0
    for community in communities:
        com = folium.FeatureGroup(name="Community " + str(i+1) , show=True)
        for source in community:
            cen = century_layers[num_centuries[j]]
            community_layers[source] = (com, i)
            info = "<h4>" + str(source) + "</h4> <h5> Century: " + centuries[j] + "</h5>" #<h5> Size: " + str(sizes_of_vertices[source]) + "</h5>
            popup1 = folium.Popup(info, max_width=300, min_width =300)
            popup2 = folium.Popup(info, max_width=300, min_width =300)

            place = Geography.objects.filter(provenance_id = provenance_ids[j]).values()[0]
            lat = place['latitude']
            long = place['longitude']
                    
            folium.CircleMarker(location=[lat , long], fill=True, color=colors[i],
                                fill_opacity=0.4, radius=3, popup=popup1).add_to(com)  #missing individual radius
            folium.CircleMarker(location=[lat , long], fill=True, color='gray',
                                fill_opacity=0.6, radius=3, popup=popup2).add_to(cen)
            j += 1
        map.add_child(com)
        i += 1


    # Lines
    
    folium.LayerControl(collapsed=False).add_to(map)

    return map
