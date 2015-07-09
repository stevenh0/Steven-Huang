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

// https://developers.google.com/maps/documentation/javascript/markers
// https://developers.google.com/maps/documentation/javascript/examples/places-searchbox
// Create the search box and link it to the UI element.

var input = /** @type {HTMLInputElement} */(
      document.getElementById('pac-input'));
map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

var searchBox = new google.maps.places.SearchBox(
    /** @type {HTMLInputElement} */(input));

var markers = [];
  // Listen for the event fired when the user selects an item from the
  // pick list. Retrieve the matching places for that item.
google.maps.event.addListener(searchBox, 'places_changed', function() {
    var places = searchBox.getPlaces();
    for (var i = 0, marker; marker = markers[i]; i++) {
      marker.setMap(null);
    }
    if (places.length == 0) {
      return;
    }

    // For each place, get the icon, place name, and location.
    markers = [];

    // Zoom in/out to show both the new location and the food vendors

    var bounds = new google.maps.LatLngBounds();
    bounds.extend(downtownVancouver);
    for (var i = 0, place; place = places[i]; i++) {
      var image = {
         url: place.icon,
         size: new google.maps.Size(71, 71),
         origin: new google.maps.Point(0, 0),
         anchor: new google.maps.Point(17, 34),
         scaledSize: new google.maps.Size(25, 25)
      };

      // Create a marker for each place.
      var marker = new google.maps.Marker({
         map: map,
         icon: image,
         title: place.name,
         position: place.geometry.location,
         click: true,
         draggable: false,
         animation: google.maps.Animation.BOUNCE// DROP
      });

    markers.push(marker);


    markers[i].addListener('click',function(){
         var infowindow = new google.maps.InfoWindow({
           content: this.title
         });
         infowindow.open(map,this);
    });

      bounds.extend(place.geometry.location);
    }
    map.fitBounds(bounds);
  });
    // Bias the SearchBox results towards places that are within the bounds of the
  // current map's viewport.

// yumi added
// http://stackoverflow.com/questions/24152420/pass-dynamic-javascript-variable-to-django-python


var URL = "/mealsOnWheels/map/";
//var URL = "/map/";

function sendFoodVendorToDjango(key){
    var data = {'foodTruckKey': key,'rating':rating};

    $.post(URL, data, function(response){
        if(response === 'success'){ alert('Yay!'); }
        else{ alert('Error! :('); }
    });
}



$(document).ready(function() {

    $('.image-popup-vertical-fit').magnificPopup({
        type:'image',
        delegate: 'a',
        closeOnContentClick: true,
        mainClass: 'mfp-img-mobile',
        image: {
            verticalFit: true
        }


    });

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

                    // yumi added
                    //$("#selected-food-truck-details h1")
                    //.html(function(){document.getElementById("rating").style.visibility="visible"});
                    rating = 0;
                    sendFoodVendorToDjango(key=data.key);

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