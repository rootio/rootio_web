map = L.map(document.getElementById('map'))

var Stamen_TonerLite = L.tileLayer('http://{s}.tile.stamen.com/toner-lite/{z}/{x}/{y}.png', {
    attribution: 'Tiles <a href="http://stamen.com">Stamen</a> | Data <a href="http://openstreetmap.org">OpenStreetMap</a> | <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC</a>',
    subdomains: 'abcd',
    minZoom: 0,
    maxZoom: 20
});

var OSM = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18
});

Stamen_TonerLite.addTo(map);
var minLat = maxLat =  minLng = maxLng = 0;

$.ajax({
    type: "GET",
    url: "/api/station",
    dataType: 'json',
    success: function (response) {
        stations = [];


        for (var i=0; i < response.objects.length; i++) {
        try{
                var station = response.objects[i];
                stations.push(stationsToLayer(station.network_id, station.name, 'on',[station.location.latitude,station.location.longitude]));
            }

           catch(err)
               {
               console.log(err)
           }
        }
        var stationGroup = L.featureGroup(stations);
        map.fitBounds(stationGroup.getBounds());
        drawStations(stations);
    }
});


function stationsToLayer(network_id, station_name, status, latlng) {
    var status_color, icon_name;
    //marker color and name of the glyphicon to display
    status_color = getStationNetworkColor(network_id);
    switch(status) {
        case 'on':
            icon_name = "ok-sign";
            break;
        case 'off':
            icon_name = 'remove-sign';
            break;
        case 'unknown':
            icon_name = 'question-sign';
            break;
        default:
            icon_name = '';
            break;
    }
    return L.marker(latlng, {
            icon: L.AwesomeMarkers.icon({color:status_color,  icon:'info', markerColor: 'green', iconColor: 'orange' }), 
            title: station_name,
            color: status_color,
            riseOnHover: true
           
        });
}

function getStationNetworkColor(network_id) {
    var colors = ['black','blue','red','green','purple','orange','darkred','darkblue','cadetblue','darkpurple','darkgreen']
    return colors[network_id % colors.length]
}


function stationPopup(feature, layer) {
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
}

function drawStations(stations) {
    for(var i = 0; i < stations.length; i++)
       {
            stations[i].addTo(map);
       }
}


$(document).ready(function() {
    $('ul#station-list a#all').on('click',
    function() {
        var $checkbox = $('ul#station-list input:checkbox');
        $checkbox.prop('checked', !$checkbox.prop('checked'));
    });
    return false;
});
