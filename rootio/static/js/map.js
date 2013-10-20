var map = L.map('map').setView([1.1975, 32.223], 6); //centered on uganda

L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18
}).addTo(map);

$.ajax({
    type: "GET",
    url: "/api/station",
    dataType: 'json',
    success: function (response) {
        stations = [];
        for (var i=0; i < response.num_results; i++) {
            var station = response.objects[i];
            //extract geo fields from api response
            var geojson = {
                "type": "Feature",
                "properties": {
                    "name": station.name,
                    "languages": station.languages,
                    "current_program": "tbd",
                    "owner": "",
                    "status": station.status
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [station.location.longitude,station.location.latitude]
                }
            }
            stations.push(geojson);
        }
        drawStations(stations);
    }
});

function drawStations(stations) {
    L.geoJson(stations,{
        onEachFeature: function bindPopup(feature, layer) {
            if (feature.properties) {
                var popupContent = '<h4>'+feature.properties.name+'</h4><ul class="status">';
                if (feature.properties.languages) {
                    var language_names = [];
                    $.each(feature.properties.languages, function(i,lang) {
                        language_names.push(lang.name);
                    });
                    popupContent += '<li>Language: '+language_names.join()+'</li>';
                }
                if (feature.properties.status) {
                    popupContent += '<li>Status: '+feature.properties.status+'</li>';
                }
                if (feature.properties.popupContent) {
                    popupContent += '<li>'+feature.properties.popupContent+'</li>';
                }
                popupContent += "</ul>";
                layer.bindPopup(popupContent);
            }
        },
        pointToLayer: function(feature, latlng) {
            var status_color, icon_name;
            //marker color and name of the glyphicon to display
            switch(feature.properties.status) {
                case 'on':
                    status_color = 'blue';
                    icon_name = "ok-sign";
                    break;
                case 'off':
                    status_color = 'red';
                    icon_name = 'remove-sign';
                    break;
                case 'unknown':
                    status_color = 'orange';
                    icon_name = 'question-sign';
                    break;
                default:
                    status_color = 'grey';
                    icon_name = '';
                    break;
            }
            return L.marker(latlng, {
                    icon: L.AwesomeMarkers.icon({
                        icon: icon_name,
                        color: status_color
                    })
                });
        }
    }).addTo(map);
}

$(document).ready(function() {
    $('ul#station-list a#all').on('click',
    function() {
        var $checkbox = $('ul#station-list input:checkbox');
        $checkbox.prop('checked', !$checkbox.prop('checked'));
    });
    return false;
});
