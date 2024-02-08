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


def get_maps(communities : list[set [str]], edges : list [tuple]):
    com_map = folium.Map(map_centre, zoom_start=5, height='70%', width='70%', tiles=None)
    tile_layer1 = folium.TileLayer(control=False)
    tile_layer1.add_to(com_map)
    cen_map = folium.Map(map_centre, zoom_start=5, height='70%', width='70%', tiles=None)
    tile_layer2 = folium.TileLayer(control=False)
    tile_layer2.add_to(cen_map)



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
    siglums = [s['siglum'] for s in used_sources]

    # Layers
    century_layers = {}
    for century in num_centuries:
        c_layer = folium.FeatureGroup(name=str(century) + ". century", show=True)
        century_layers[century] = c_layer
        cen_map.add_child(c_layer)

    community_layers = {}
    sources_coordinates = {}

    # Points
    sources_with_no_geo = []
    i, j = 0, 0
    for community in communities:
        com = folium.FeatureGroup(name="Community " + str(i+1) , show=True)
        for source in community:
            cen = century_layers[num_centuries[j]]
            community_layers[source] = (com, i)
            if Geography.objects.filter(provenance_id = provenance_ids[j]).exists():
                place = Geography.objects.filter(provenance_id = provenance_ids[j]).values()
                lat = place[0]['latitude']
                long = place[0]['longitude']
                sources_coordinates[source] = [lat, long]
                provenance = Sources.objects.filter(provenance_id = provenance_ids[j]).values()[0]['provenance']
                info = "<h5> <a href=  \"{}\"  target=\"_blank\" rel=\"noopener noreferrer\"> {} </a>".format(source, source) + "</h5> <h5> Provenance: " + provenance + "</h5> <h5> Century: " + centuries[j] + "</h5> <h5> Siglum: " + siglums[j] + "</h5>"
                popup1 = folium.Popup(info, max_width=300, min_width =300)
                popup2 = folium.Popup(info, max_width=300, min_width =300)

            else:
                sources_with_no_geo.append(source)
                j += 1
                continue
                    
            folium.CircleMarker(location=[lat , long], fill=True, color=colors[i],
                                fill_opacity=0.4, radius=8, popup=popup1).add_to(com)  #missing individual radius
            folium.CircleMarker(location=[lat , long], fill=True, color=colors[i],
                                fill_opacity=0.6, radius=8, popup=popup2).add_to(cen)
            j += 1
        
        com_map.add_child(com)
        i += 1


    # Lines
    for line in edges:
        if line[0] not in sources_with_no_geo and line[1] not in sources_with_no_geo: # there is a way of drawing it
            coord_1 = sources_coordinates[line[0]]
            coord_2 = sources_coordinates[line[1]]
            popup1 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)
            popup2 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)
            if community_layers[line[0]][1] == community_layers[line[1]][1]:
                color = colors[community_layers[line[0]][1]]
                com = community_layers[line[0]][0]
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*6, popup=popup1, color=color).add_to(com)
            else:
                color = 'black'
                com1 = community_layers[line[0]][0]
                com2 = community_layers[line[1]][0]
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*6, popup=popup1, color=color).add_to(com1)
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*6, popup=popup2, color=color).add_to(com2)
            
    
    folium.LayerControl(collapsed=False).add_to(com_map)
    folium.LayerControl(collapsed=False).add_to(cen_map)
    return com_map, cen_map
