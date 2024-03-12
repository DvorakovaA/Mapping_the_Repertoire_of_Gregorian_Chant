// Function for construction of leaflet maps given map_data

const center = [47.466667, 11.166667]

function getMaps(map_data) {
    /** 
     * Function for construction of two lefalet map objects:
     * com_map as map with layer control for given communities
     * cen_map as map with layer control for centuries of origin of sources
    */
    // Get basic maps with OpenStreetMap map layer
    var com_map = L.map('com_map').setView(center, 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 
        { 
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(com_map);

    var cen_map = L.map('cen_map').setView(center, 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 
        { 
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(cen_map);
    
    
    // We have data to show
    if (map_data.num_of_communities) {
        // Get ready layer control for community layers
        var comLayerControl = L.control.layers(null, null, {collapsed:false});
        var com_layers = {}
        // Layer for shared edges
        com_layers['shared'] = L.layerGroup();
        comLayerControl.addOverlay(com_layers['shared'], "All shared edges");
        com_layers['shared'].addTo(com_map);
        // Create layer for each community and add it to layerControl
        for(let i = 0; i < map_data.num_of_communities; i++) {
            const com_name = "Community " + (i+1);
            var l = L.layerGroup();
            com_layers[i] = l;
            comLayerControl.addOverlay(l, com_name)
            l.addTo(com_map);
        }
        // Get ready layer control for century layers
        var cenLayerControl = L.control.layers(null, null, {collapsed:false});
        var cen_layers = {}
        // Layer for shared edges
        cen_layers['shared'] = L.layerGroup();
        cenLayerControl.addOverlay(cen_layers['shared'], "All shared edges");
        cen_layers['shared'].addTo(cen_map);
        // Create layer for each century group and add it to layerControl
        //var cen_name;
        for(century of map_data.used_centuries) {
            var cen_name = century + "th century";
            if (century == "unknown") {
                cen_name = "unknown";
            }
            //else {
             //   cen_name = century + "th century"; }

            var l = L.layerGroup();
            cen_layers[century] = l;
            cenLayerControl.addOverlay(l, cen_name);
            l.addTo(cen_map);
        }

        // First add edges
        for (const line of map_data.edges) {
            // Check if we have coordinates
            if(! map_data.no_prov_sources.includes(line[0]) &&  ! map_data.no_prov_sources.includes(line[1])) {
                const lat1 = map_data.map_sources_dict[line[0]].lat
                const long1 = map_data.map_sources_dict[line[0]].long
                const lat2 = map_data.map_sources_dict[line[1]].lat
                const long2 = map_data.map_sources_dict[line[1]].long
                const line_popup = "<h5> <a href="+line[0]+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[line[0]].siglum+"</a>" + " : " +  line[2] +
                                   "<br> <a href="+line[0]+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[line[1]].siglum+"</a>" + " : " +  line[3] + 
                                   "<br> Jaccard distance: " + line[4]['weight'] + "</h5>";
                const com_id = map_data.map_com_info[line[0]];

                // Same community
                if (com_id == map_data.map_com_info[line[1]]) {
                    var edge = L.polyline([[lat1, long1], [lat2, long2]], {color : map_data.colors[com_id], weight : line[4]['weight']*1.8 + 1.4});
                    edge.bindPopup(line_popup);
                    edge.addTo(com_layers[com_id]);
                }
                // Edge shared between century groups
                else {
                    var edge1 = L.polyline([[lat1, long1], [lat2, long2]], {color : 'black', weight : line[4]['weight']*1.8 + 1.4});
                    edge1.bindPopup(line_popup);
                    edge1.addTo(com_layers[com_id]);
                    edge1.addTo(com_layers['shared']);

                    var edge2 = L.polyline([[lat1, long1], [lat2, long2]], {color : 'black', weight : line[4]['weight']*1.8 + 1.4});
                    edge2.bindPopup(line_popup);
                    edge2.addTo(com_layers[map_data.map_com_info[line[1]]]);
                    edge2.addTo(com_layers['shared']);
                }
                // Same century group
                if(map_data.map_cen_info[line[0]] == map_data.map_cen_info[line[1]])
                {
                    var edge = L.polyline([[lat1, long1], [lat2, long2]], {color : map_data.colors[com_id], weight : line[4]['weight']*1.8 + 1.4});
                    edge.bindPopup(line_popup);
                    edge.addTo(cen_layers[map_data.map_cen_info[line[0]]]);
                }
                // Edge shared between century groups
                else {
                    var edge1 = L.polyline([[lat1, long1], [lat2, long2]], {color : 'black', weight : line[4]['weight']*1.8 + 1.4});
                    edge1.bindPopup(line_popup);
                    edge1.addTo(cen_layers[map_data.map_cen_info[line[0]]]);
                    edge1.addTo(cen_layers['shared']);

                    var edge2 = L.polyline([[lat1, long1], [lat2, long2]], {color : 'black', weight : line[4]['weight']*1.8 + 1.4});
                    edge2.bindPopup(line_popup);
                    edge2.addTo(cen_layers[map_data.map_cen_info[line[1]]]);
                    edge2.addTo(cen_layers['shared']);
                }
                
            }
        }

        // Add sources markers
        for(source in map_data.map_com_info) {
            const lat = map_data.map_sources_dict[source].lat
            const long = map_data.map_sources_dict[source].long
            const marker_popup = "<a href="+source+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[source].siglum + "</a>" + 
                                  "<br> <b>" + map_data.map_sources_dict[source].title +   
                                  "</b> <br> Provenance: " + map_data.map_sources_dict[source].provenance + 
                                  "<br> Century: " + map_data.map_sources_dict[source].century;
            // Community map
            var point1 = L.circleMarker([lat, long], {radius: 10, color: map_data.colors[map_data.map_com_info[source]]});
            point1.bindPopup(marker_popup);
            point1.addTo(com_layers[map_data.map_com_info[source]]);
            // Century map
            var point2 = L.circleMarker([lat, long], {radius: 10, color: map_data.colors[map_data.map_com_info[source]]});
            point2.bindPopup(marker_popup);
            point2.addTo(cen_layers[map_data.map_cen_info[source]]);
        }
    }

    comLayerControl.addTo(com_map);
    cenLayerControl.addTo(cen_map);

    return com_map, cen_map;
}