// File with two functions:
//  getMaps - function for construction of leaflet maps given map_data
//  getMapOfAllSources - function for construction of leaflet map of all provenances given map_data_all

// Center of returned map (centre of Europe somewhere in Slovenia, we do not need to view Scandinavia)
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
    
    // Pane to preserve good order on z axis (points on top of edges)
    com_map.createPane("point");
    com_map.createPane("line");
    com_map.getPane("point").style.zIndex = 650;
    cen_map.createPane("point");
    cen_map.createPane("line");
    cen_map.getPane("point").style.zIndex = 650;

    
    // We have data to show
    if (map_data.num_of_communities) {
        //Renderers speed up display via Canvas (instead of default SVG)
        var comRenderer = L.canvas();
        var cenRenderer = L.canvas(); 

        // Get ready layer control for community layers
        var comLayerControl = L.control.layers(null, null, {collapsed:false});
        var com_layers = {}
        // Layer for all edges
        var allCom = L.layerGroup();
        com_layers['all'] = allCom;
        //com_layers['all'].addTo(com_map); - no add means it is not defaultly checked
        comLayerControl.addOverlay(com_layers['all'], "All edges");
        // Layer for shared edges
        var sharedCom = L.layerGroup();
        com_layers['shared'] = sharedCom;
        //com_layers['shared'].addTo(com_map); - no add means it is not defaultly checked
        comLayerControl.addOverlay(com_layers['shared'], "All shared edges");
        // Create layer for each community and its edges
        // Add it to layerControl
        for(let i = 0; i < map_data.num_of_communities; i++) {
            const com_name = "Community " + (i+1);
            var l = L.layerGroup();
            com_layers[i] = l;
            com_layers[i].addTo(com_map);
            comLayerControl.addOverlay(com_layers[i], com_name);
            
            var lE = L.layerGroup();
            var edgeKey = i+"edges";
            com_layers[edgeKey] = lE;
            //com_layers[edgeKey].addTo(com_map); - no add means it is not defaultly checked
            comLayerControl.addOverlay(com_layers[edgeKey], com_name+" edges");
        }

        // Get ready layer control for century layers
        var cenLayerControl = L.control.layers(null, null, {collapsed:false});
        var cen_layers = {}

        for(century of map_data.used_centuries) {
            var cen_name = century + "th century";
            if (century == "unknown") {
                cen_name = "unknown";
            }
            var l = L.layerGroup();
            cen_layers[century] = l;
            l.addTo(cen_map);
            cenLayerControl.addOverlay(l, cen_name);
        }

        // First add edges to particular layers
        for (const line of map_data.edges) {
            // Check if we have coordinates for such edge (both ends have known provenance)
            if(! map_data.no_prov_sources.includes(line[0]) &&  ! map_data.no_prov_sources.includes(line[1])) {
                // Collect info
                const lat1 = map_data.map_sources_dict[line[0]].lat
                const long1 = map_data.map_sources_dict[line[0]].long
                const lat2 = map_data.map_sources_dict[line[1]].lat
                const long2 = map_data.map_sources_dict[line[1]].long
                const line_popup = "<a href="+line[0]+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[line[0]].siglum+"</a>" + " : " +  line[2] +
                                   "<br> <a href="+line[1]+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[line[1]].siglum+"</a>" + " : " +  line[3] + 
                                   "<br> Weight: " + line[4]['weight'];
                const com_id = map_data.map_com_info[line[0]];
                var weight = 1.4;
                if (line[4]['weight'] != '-') {
                    weight = line[4]['weight']*1.8 + 1.3;
                }

                // Same community
                if (com_id == map_data.map_com_info[line[1]]) {
                    var edge = L.polyline([[lat1, long1], [lat2, long2]], {renderer: comRenderer, color : map_data.colors[com_id], weight : weight, pane : "line"});
                    edge.bindPopup(line_popup);
                    edge.addTo(com_layers[com_id+"edges"]);
                    edge.addTo(com_layers['all']);
                }
                // Edge shared between community groups
                else {
                    var edge1 = L.polyline([[lat1, long1], [lat2, long2]], {renderer: comRenderer, color : 'black', weight : weight, pane : "line"});
                    edge1.bindPopup(line_popup);
                    edge1.addTo(com_layers['shared']);
                    edge1.addTo(com_layers['all']);
                }
            }
        }

        // Add sources markers
        for(source in map_data.map_com_info) {
            // Collect info
            const lat = map_data.map_sources_dict[source].lat
            const long = map_data.map_sources_dict[source].long
            const marker_popup = "<a href="+source+" target=\"_blank'\" rel=\"noopener noreferrer\">"+map_data.map_sources_dict[source].siglum + "</a>" + 
                                  "<br> <b>" + map_data.map_sources_dict[source].title +   
                                  "</b> <br> Provenance: " + map_data.map_sources_dict[source].provenance + 
                                  "<br> Century: " + map_data.map_sources_dict[source].century;
            
            // Markers
            if (map_data.map_sources_dict[source].cursus === 'Unknown') {
                // Community map
                var point1 = L.circleMarker([lat, long], {renderer : comRenderer, radius: 10, color : map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point1.bindPopup(marker_popup);
                point1.addTo(com_layers[map_data.map_com_info[source]]);
                // Century map
                var point2 = L.circleMarker([lat, long], {renderer : cenRenderer, radius: 10, color : map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point2.bindPopup(marker_popup);
                point2.addTo(cen_layers[map_data.map_cen_info[source]]);
            }
            else if (map_data.map_sources_dict[source].cursus === 'Monastic') {
                // Community map
                var point1 = L.shapeMarker([lat, long], {renderer : comRenderer, shape : 'square', radius: 8.5, color: map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point1.bindPopup(marker_popup);
                point1.addTo(com_layers[map_data.map_com_info[source]]);
                // Century map
                var point2 = L.shapeMarker([lat, long], {renderer : cenRenderer, shape : 'square', radius: 8.5, color: map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point2.bindPopup(marker_popup);
                point2.addTo(cen_layers[map_data.map_cen_info[source]]);
            }
            else { //Secular and Romanum
                // Community map
                var point1 = L.shapeMarker([lat, long], {renderer: comRenderer, shape : 'triangle', radius: 8.5, color: map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point1.bindPopup(marker_popup);
                point1.addTo(com_layers[map_data.map_com_info[source]]);
                // Century map
                var point2 = L.shapeMarker([lat, long], {renderer: cenRenderer, shape : 'triangle', radius: 8.5, color: map_data.colors[map_data.map_com_info[source]], pane : "point"});
                point2.bindPopup(marker_popup);
                point2.addTo(cen_layers[map_data.map_cen_info[source]]);
            }
        }
        // Finally add layer controls (and layers in them) to the maps
        comLayerControl.addTo(com_map);
        cenLayerControl.addTo(cen_map);
    }

    return {com_map, cen_map};
}



function getMapOfAllBasic(map_all_data) {
    // Get map
    var complete_map = L.map('com_map').setView(center, 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 
        { 
        attribution: '&copy; <a href="http://weww.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(complete_map);


    for (const point of map_all_data) {
        //Collect data
        const lat = point[1];
        const long = point[2];
        const popup_info = point[0];
        
        // Create marker for source
        var marker = L.circleMarker([lat, long], {radius : 8, color : '#2e8bc0'});
        marker.bindPopup(popup_info);
        marker.addTo(complete_map);
    }

    return complete_map;
}


function getMapOfAllInformed(map_all_data) {
    // Get map
    var complete_map = L.map('com_map').setView(center, 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', 
        { 
        attribution: '&copy; <a href="http://weww.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(complete_map);

    // Data to be parsed:
    //      all_map_data = {'provenance_name' : [lat, long, [[url, siglum], [url, siglum], ...]], '' : [], ...}
    for (var point in map_all_data) {
        const info = map_all_data[point];
        var popup_info = "<b>" + point + "</b><br>";

        //Collect data
        const lat = info[0];
        const long = info[1];
        for (source of info[2]) {
            popup_info += "<a href="+source[0]+" target=\"_blank'\" rel=\"noopener noreferrer\">"+source[1]+ "</a><br>"
        }
        
        // Create marker for source
        var marker = L.circleMarker([lat, long], {radius : 8, color : '#2e8bc0'});
        marker.bindPopup(popup_info);
        marker.addTo(complete_map);
    }
}