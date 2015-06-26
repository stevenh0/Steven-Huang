<!--http://stackoverflow.com/questions/15144691/google-maps-multiple-marker-from-extern-json-->
var map;
var downtownVancouver = new google.maps.LatLng(49.28,-123.12);

function initialize() {
  var mapOptions = {
    zoom: 14,
    center: downtownVancouver,
    mapTypeId:google.maps.MapTypeId.ROADMAP
  }

map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

$(document).ready(function() {
    $.getJSON("/mealsOnWheels/food_trucks", function(food_trucks_json) {
        $.each(food_trucks_json, function(key, data) {
            var latLng = new google.maps.LatLng(data.latitude, data.longitude);

            // Creating a marker and putting it on the map
            var marker = new google.maps.Marker({
            position: latLng,
            title: data.name
                });

                marker.setMap(map);
                var infowindow = new google.maps.InfoWindow({
					content: data.name
					});

                google.maps.event.addListener(marker, 'click', function() {
					infowindow.open(map,marker);

					$( "#selected-food-truck-details p" )
					.html( data.description );
					$( "#selected-food-truck-details h3" )
					.html( data.name );

                    $( "#instafeed")
                    .html ( "" );
					run(data.name);

				});

            });
        });
    });

    <!--http://stackoverflow.com/questions/743214/how-do-i-resize-a-google-map-with-javascript-after-it-has-loaded-->
	$(window).resize(function() {
        google.maps.event.trigger(map, "resize");
    });
};

google.maps.event.addDomListener(window, 'load', initialize);