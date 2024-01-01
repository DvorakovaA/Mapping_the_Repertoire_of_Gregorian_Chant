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

    # Layers
    century_layers = {}
    centuries = [Sources.objects.filter(drupal_path = source) for source in sources_dict.keys()]
    for century in centuries:
        print(century)
        c_layer = folium.FeatureGroup(name=str(century) + ". century", show=False)
        century_layers[century] = c_layer
        map.add_child(c_layer)

    community_layers = {}

    # Points

    # Lines
    
    folium.LayerControl(collapsed=False).add_to(map)

    return map
