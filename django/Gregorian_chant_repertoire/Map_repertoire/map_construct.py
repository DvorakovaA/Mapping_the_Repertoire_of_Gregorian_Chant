'''
Module providing main function get_maps
that returns two objects of folium maps visualization of given sources communities,
one for community display and one for century display
'''

import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, rgb2hex

from .models import Sources, Geography

map_centre = [47.466667, 11.166667] # Centre of returned maps


def get_maps(communities : list[set [str]], edges : list [tuple]):
    '''
    Given communities of sources and info about conections beetween sources
    function constructs two folium map objects one with community layers and one
    with layers based on centuries of origin
    '''
    # Get map objects and assign them map layer
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
    
    # Get dict (-> source : info_about_source) for sources in communities
    sources_dict = {}
    for community in communities:
        for source in community:
            sources_dict[source] = Sources.objects.filter(drupal_path = source).values()[0]


    # Displaying layers and dicts that hold them
    numeric_centuries = [sources_dict[s]['num_century'] for s in sources_dict.keys()]
    century_layers = {}
    sorted_cen = sorted(numeric_centuries)
    for numeric_cen in sorted_cen:
        c_layer = folium.FeatureGroup(name=str(numeric_cen) + ". century", show=True)
        century_layers[numeric_cen] = c_layer
        cen_map.add_child(c_layer)

    community_layers = {}

    coordinates_of_sources = {}

    # Points
    sources_with_no_geo = []
    i, j = 0, 0
    for community in communities:
        com = folium.FeatureGroup(name="Community " + str(i+1) , show=True)
        for source in community:
            cen = century_layers[numeric_centuries[j]]
            community_layers[source] = (com, i)
            if Geography.objects.filter(provenance_id = sources_dict[source]['provenance_id']).exists():
                place = Geography.objects.filter(provenance_id = sources_dict[source]['provenance_id']).values()
                lat = place[0]['latitude']
                long = place[0]['longitude']
                coordinates_of_sources[source] = [lat, long]
                provenance = Sources.objects.filter(provenance_id = sources_dict[source]['provenance_id']).values()[0]['provenance']
                info = "<h5> <a href=  \"{}\"  target=\"_blank\" rel=\"noopener noreferrer\"> {} </a>".format(source, source) + "</h5> <h5> Provenance: " + provenance + "</h5> <h5> Century: " + sources_dict[source]['century'] + "</h5> <h5> Siglum: " + sources_dict[source]['siglum'] + "</h5>"
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
            coord_1 = coordinates_of_sources[line[0]]
            coord_2 = coordinates_of_sources[line[1]]

            popup1 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)
            popup2 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)
            popup3 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)
            popup4 = folium.Popup('<h5> Jaccard distance: ' + str(line[2]['weight']) + '</h5>', max_width=300)

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
            
            if sources_dict[line[0]]['num_century'] == sources_dict[line[1]]['num_century']:
                color = colors[community_layers[line[0]][1]]
                cen = century_layers[sources_dict[line[0]]['num_century']]
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*5, popup=popup3, color=color).add_to(cen)
            else:
                color = 'black'
                cen1 = century_layers[sources_dict[line[0]]['num_century']]
                cen2 = century_layers[sources_dict[line[1]]['num_century']]
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*5, popup=popup3, color=color).add_to(cen1)
                folium.PolyLine(locations=[coord_1, coord_2], weight=line[2]['weight']*5, popup=popup4, color=color).add_to(cen2)


    folium.LayerControl(collapsed=False).add_to(com_map)
    folium.LayerControl(collapsed=False).add_to(cen_map)

    missing_info = "<div>" + str(len(sources_with_no_geo)) + " sources with unknown provenance </div>"
    com_map.get_root().html.add_child(folium.Element(missing_info))
    cen_map.get_root().html.add_child(folium.Element(missing_info))

    return com_map, cen_map
