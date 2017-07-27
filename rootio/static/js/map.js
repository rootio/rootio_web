map = L.map(document.getElementById('map')) //.setView([1.1975, 32.223], 6); //centered on uganda

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

        try{
        for (var i=0; i < response.objects.length; i++) {
                var station = response.objects[i];
                stations.push(stationsToLayer(station.name, 'on',[station.latitude,station.longitude]));
            }
           }
           catch(err)
               {alert(err)}
        
        var stationGroup = L.featureGroup(stations);
        map.fitBounds(stationGroup.getBounds());
        drawStations(stations);
    }
});


function stationsToLayer(station_name, status, latlng) {
    var status_color, icon_name;
    //marker color and name of the glyphicon to display
    switch(status) {
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
                color: status_color,
                title: 'station_name',
                alt: 'station_name',
                riseOnHover: true
 
            })
        });
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
