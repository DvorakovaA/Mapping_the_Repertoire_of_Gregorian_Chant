import './style.css';
import {Map, View} from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

var vectorSource = new ol.source.Vector({});

const map = new ol.Map({
  layers: [
    new TileLayer({
      source: new OSM()
    }),
      new ol.layer.Vector({
          source: vectorSource
      })
  ],
  target: 'map',
  view: new ol.View({
    center: [-11000000, 4600000],
    zoom: 4
  })
});

var thing = new ol.geom.Polygon( [[
    ol.proj.transform([-16,-22], 'EPSG:4326', 'EPSG:3857'),
    ol.proj.transform([-44,-55], 'EPSG:4326', 'EPSG:3857'),
    ol.proj.transform([-88,75], 'EPSG:4326', 'EPSG:3857')
]]);
var featurething = new ol.Feature({
    name: "Thing",
    geometry: thing
});
vectorSource.addFeature( featurething );

/*
const map = new Map({
  target: 'map',
  layers: [
    new TileLayer({
      source: new OSM()
    })
  ],
  view: new View({
    center: [0, 0],
    zoom: 2
  })
});

var vectorLayer = new ol.layer.Vector({
  source: new ol.source.GeoJSON({
    
  })
});

// Geometries
var point = new ol.geom.Point(
  ol.proj.transform([3,50], 'EPSG:4326', 'EPSG:3857')
);
var circle = new ol.geom.Circle(
  ol.proj.transform([2.1833, 41.3833], 'EPSG:4326', 'EPSG:3857'),
  1000000
);

// Features
var pointFeature = new ol.Feature(point);
var circleFeature = new ol.Feature(circle);

// Source
var vectorSource = new ol.source.Vector({
  projection: 'EPSG:4326'
});
vectorSource.addFeatures([pointFeature, circleFeature]);

// Vector layer
var vectorLayer = new ol.layer.Vector({
source: vectorSource
});

// Add Vector layer to map
map.addLayer(vectorLayer);
*/