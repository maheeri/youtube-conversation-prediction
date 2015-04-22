  // ----------------- Global -----------------

// restaurant name -> data
var restaurant_data = {}
// restaurant name -> marker
var markers = {}
// restaurant name -> info content
var info_content = {}

// resused infowindow object
var infowindow = new google.maps.InfoWindow({
  content: '',
});

var view_port_dim;

$(function() {
  $main_container = $('.main_container');
  $input_panel = $('#input_panel');
  $input_form = $('#input_form');
  $loc_input_field = $('#loc_input_field');
  $dist_input_field = $('#dist_input_field');
  $error_text = $('.error_text');

  $info_panel = $('#info_panel');
  $results = $('#results')
  $map_canvas = $('#map-canvas');
  $spinner = $('#spinner');
  $result_count = $('#result_count');
  $display_input = $('#display_input');
  $back_button = $('#back_button');
  $results_button = $('#results_button');

  // Set container dimensions
  view_port_dim = {x: $(window).width(), y: $(window).height()};
  $main_container.height(view_port_dim.y);

  // Initialize google maps
  var map = initialize_map()
  var infowindow = new google.maps.InfoWindow({
    content: ''
  });

  var $selected_result = null;

  // ----------------- Event handlers -----------------

  $input_form.submit(function(event) {
    event.preventDefault();
    var input = $loc_input_field.val();
    var dist = $dist_input_field.val();

    var error = '';
    if(!input) {
      error = 'No input location!';
    } else if (!dist || isNaN(dist)) {
      error = 'Distance must be a valid number!';
    } else {
      console.log('Searching restaurants...');
      find_nearest(input, parseFloat(dist), map, infowindow);
    }

    if(error) {
      $error_text.text(error).show().delay(2000).fadeOut(1000);
    }
  });

  $results.on('click', 'li', function(event) {
    if($selected_result == $(this)) return;

    // highlight this selection and open the info
    if($selected_result) {
      $selected_result.find('.name').removeClass('orange');
    }
    $(this).find('.name').addClass('orange');

    $selected_result = $(this);
    var name = $(this).data('name');
    open_info(markers[name], map, infowindow);
  });

  $back_button.on('click', function(event) {
    // Hide input form and display results
    $info_panel.fadeOut('fast', function() {
      $input_form.fadeIn('fast');
    });
  })

  $results_button.on('click', function(event) {
    download_results();
  })
});

// ------------------------ Functions ------------------------

function initialize_map() {
  var mapOptions = {
    zoom: 15
  };
  var map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);

  // Try HTML5 geolocation
  if(navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

      var infowindow = new google.maps.InfoWindow({
        map: map,
        position: pos,
        content: '<div class="marker_label">Your location.</div>'
      });

      map.setCenter(pos);
    }, function() {
      handleNoGeolocation(true);
    });
  } else {
    // Browser doesn't support Geolocation
    handleNoGeolocation(false);
  }

  return map;
}

function handleNoGeolocation(errorFlag) {
  if (errorFlag) {
    var content = 'Error: The Geolocation service failed.';
  } else {
    var content = 'Error: Your browser doesn\'t support geolocation.';
  }
  var options = {
    map: map,
    position: new google.maps.LatLng(60, 105),
    content: content
  };
  var infowindow = new google.maps.InfoWindow(options);
  map.setCenter(options.position);
}

function find_nearest(input, dist, map, infowindow) {
  $spinner.show(500);
  info_content[input] = $('<div></div>').html(input);

  $.ajax({
    type: 'POST',
    url: '/find_restaurants',
    data: {input_location: input, dist: dist},
  }).done(function(data) {
    console.log(data);
    $spinner.hide(500);
    if(data) {
      display_results(input, data);
      place_markers(data, input, map, infowindow);
    } else {
      console.log('Invalid response');
    }
  }).fail(function(error, status) {
    $spinner.hide(500);
    alert(error.responseText + ' ' + status);
  });
}

function display_results(input, data) {
  var results = data['results']

  $results.html('');
  for(var restaurant in results) {
    restaurant_data = results[restaurant];

    var $entry = $('<li></li>')
      .addClass('list-group-item').data('name', restaurant)
      .html('<div class="name">' + restaurant + '</div>');

    var $details = $('<div></div>').addClass('restaurant_item').html(
      '<div class="name orange">' + restaurant + '</div>' +
      '<div class="details">' +
      '<div><b>Address: </b>' + restaurant_data['loc'] + '</div>' +
      '<div><b>Coordinates: </b>' + restaurant_data['latlng']['lat'] + ', ' + restaurant_data['latlng']['lng'] + '</div>' +
      '<div><b>Distance: </b>' + restaurant_data['dist'] + ' miles</div></div>')
    info_content[restaurant] = $details;

    $results.append($entry);
  }

  // Display restaurant count
  $result_count.html(Object.keys(results).length);
  // Reiterate input location
  $display_input.html(input);

  // Hide input form and display results
  $input_form.fadeOut('fast', function() {
    $info_panel.fadeIn('fast');
  });

  $results.css({'max-height':
  (view_port_dim.y - $('.info_text').height() - $('.results_text').height() - 80) + 'px'});
}

function place_markers(data, input, map, infowindow) {
  var results = data['results'];

  // Clear markers
  for(var r in markers) {
    markers[r].setMap(null);
  }

  // Add restaurant markers
  for(var restaurant in results) {
    var restaurant_data = results[restaurant];
    var latlng = restaurant_data['latlng'];
    latlng = new google.maps.LatLng(latlng['lat'], latlng['lng']);
    addMarker(latlng, restaurant, map);
  }

  // Add input location marker
  var latlng = data['input_data']['latlng'];
  latlng = new google.maps.LatLng(latlng['lat'], latlng['lng']);
  
  var marker = addMarker(latlng, input, map);
  open_info(marker, map, infowindow);

  // Center map on input location
  map.setCenter(latlng);
}

// Add a marker to the map
function addMarker(pos, title, map) {
  var marker = new google.maps.Marker({
    position: pos,
    map: map,
    animation: google.maps.Animation.DROP,
    title: title,
  });

  google.maps.event.addListener(marker, 'click', function() {
    open_info(this, map, infowindow);
  });

  // Store markers for future reference
  markers[title] = marker;
  return marker;
}

// Open an info window for this marker
// if the marker is for the input data, don't display details
function open_info(marker, map, infowindow) {
  var content = $('<div></div>').addClass('marker_label').html(info_content[marker.title].clone()[0]);
  infowindow.setContent(content[0]);
  infowindow.open(map, marker);
}

function download_results() {
  $spinner.show(500);
  $.ajax({
    type: 'GET',
    url: '/results',
  }).done(function(data) {
    $spinner.hide(500);
    if(data) {
      // save file
      var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
      saveAs(blob, 'queries.txt');
    } else {
      console.log('Invalid response');
    }
  }).fail(function(error, status) {
    $spinner.hide(500);
    alert(error.responseText + ' ' + status);
  });
}
