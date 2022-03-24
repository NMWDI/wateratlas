// import * as nmbg_locations from './nmbg_locations.json'


var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
})

var map = L.map('map', {
        preferCanvas: true,
        updateWhenZooming: false,
        updateWhenIdle: true,
        layers: [osm]
    }
)
map.setView([34.359593, -106.906871], 7);

var layerControl = L.control.layers({"osm": osm}, null).addTo(map);

var use_cluster = false;

$.getJSON("st2locations").then(
    function (data) {
        var options=data['options'];
        var fuzzy_options=data['fuzzy_options'];
        var markers=data['markers'];
        var fuzzy_markers=data['fuzzy_markers'];
        var markers_layer = L.geoJson(markers, {
            pointToLayer: function (feature, latln){
                var marker = L.circleMarker(latln, options)
                return marker
            }
        })

            if (use_cluster){
                var cluster= L.markerClusterGroup();
                cluster.addLayer(markers_layer)
            }else{
                cluster = markers_layer
            }

            map.addLayer(cluster)
            layerControl.addOverlay(cluster, 'ST2')


            var fuzzy_layer = L.geoJson(fuzzy_markers, fuzzy_options)
            layerControl.addOverlay(fuzzy_layer, 'OSE RealTime')
    })

$.getJSON("nmenvlocations").then(
function (data) {
var options=data['options'];
var markers=data['markers'];
var layer = L.geoJson(markers, {
    pointToLayer: function (feature, latln){
        var marker = L.circleMarker(latln, options)
        return marker
    }
})
    if (use_cluster){
        var cluster= L.markerClusterGroup();
        cluster.addLayer(layer)
    }else{
        cluster = layer
    }
    map.addLayer(cluster)
    layerControl.addOverlay(cluster, 'NMENV')


})

$.getJSON("oselocations").then(
function (data) {
var options=data['options'];
var markers=data['markers'];
var layer = L.geoJson(markers, {
    pointToLayer: function (feature, latln){
        var marker = L.circleMarker(latln, options)
        return marker
    }
})
        if (use_cluster){
            var cluster= L.markerClusterGroup({'chunkedLoading': true});
            cluster.addLayers(layer)

        }else{
            cluster = layer
        }

        map.addLayer(cluster)
        layerControl.addOverlay(cluster, 'OSE PODS')
})



