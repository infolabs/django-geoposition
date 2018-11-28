if (jQuery != undefined) {
  var django = {
    'jQuery': jQuery,
  }
}

(function($) {
  $(document).ready(function() {

      var mapDefaults = {
        center: [55.76, 37.64],
        zoom: 15,
        type: 'yandex#map',
        controls: [
          'fullscreenControl',
          'geolocationControl',
          'zoomControl',
        ]
      };

      var typeSelectorDefaults = {
        mapTypes: [
          'yandex#map',
          'yandex#satellite'
        ],
        options: {
          panoramasItemMode: 'off'
        }
      };

      var placemarkDefaults = {
        geometry: [55.76, 37.64],
        properties: {},
        options: {
          draggable: true,
        }
      };

      $('.geoposition-widget').each(function() {
        var $container = $(this),
            $mapContainer = $('<div class="geoposition-map" />'),
            $addressRow = $('<div class="geoposition-address" />'),
            $searchRow = $('<div class="geoposition-search" />'),
            $searchInput = $('<input>', {'type': 'search', 'placeholder': 'Start typing an address …'}),
            $showMap = $container.find('.geoposition-show-map span'),
            $latitudeField = $container.find('input.geoposition:eq(0)'),
            $longitudeField = $container.find('input.geoposition:eq(1)'),
            latitude = parseFloat($latitudeField.val()) || null,
            longitude = parseFloat($longitudeField.val()) || null,
            mapUrl,
            map,
            mapOptions,
            mapCustomOptions,
            placemarkOptions,
            placemarkCustomOptions,
            placemark;

        mapUrl = $container.attr('data-map-url');
        mapCustomOptions = JSON.parse($container.attr('data-map-options'));
        placemarkCustomOptions = JSON.parse($container.attr('data-marker-options'));

        function doGeocode() {
          ymaps.geocode(
            placemark.geometry.getCoordinates(),
            {kind: 'house', results: 1}
          ).then(function (results) {
            $addressRow.text('');
            var geoObjs = results.geoObjects.toArray();
            if (geoObjs.length) {
              var props = geoObjs[0].properties.getAll();
              $addressRow.text(props.text);
            }
          });
        }

        function doSearch() {
          $searchInput.parent().find('ul.geoposition-results').remove();
          ymaps.geocode(
            $searchInput.val(),
            {kind: 'house', results: 10}
          ).then(function(results) {
            var geoObjs = results.geoObjects.toArray();
            if (geoObjs.length) {
              var updatePosition = function(geoObj) {
                var props = geoObj.properties.getAll();
                var center = geoObj.geometry.getCoordinates();
                map.setBounds(props.boundedBy);
                placemark.geometry.setCoordinates(center);
                placemark.events.fire("dragend");
              };
              if (geoObjs.length == 1) {
                updatePosition(geoObjs[0]);
              } else {
                var $ul = $('<ul />', {'class': 'geoposition-results'});
                $.each(geoObjs, function(i, geoObj) {
                  var props = geoObj.properties.getAll();
                  var $li = $('<li />');
                  $li.text(props.text);
                  $li.bind('click', function() {
                    updatePosition(geoObj);
                    $li.closest('ul').remove();
                  });
                  $li.appendTo($ul);
                });
                $searchInput.after($ul);
              }
            }
          });
        }

        mapOptions = $.extend({}, mapDefaults, mapCustomOptions);
        if (!(latitude === null && longitude === null && mapOptions['center'])) {
          mapOptions['center'] = [latitude, longitude];
        }
        if (!mapOptions['zoom']) {
          mapOptions['zoom'] = latitude && longitude ? 15 : 1;
        }

        $latitudeField.closest('tr').hide();
        $longitudeField.closest('tr').hide();

        function showMap() {
          $latitudeField.closest('tr').show();
          $longitudeField.closest('tr').show();

          $searchInput.appendTo($searchRow);
          $container.append($searchRow, $mapContainer, $addressRow);
          $mapContainer.css('height', $container.attr('data-map-widget-height') + 'px');

          var autoSuggestTimer = null;
          $searchInput.bind('keydown', function(e) {
            if (autoSuggestTimer) {
              clearTimeout(autoSuggestTimer);
              autoSuggestTimer = null;
            }
            // if enter, search immediately
            if (e.keyCode == 13) {
              e.preventDefault();
              doSearch();
            }
            else {
              // otherwise, search after a while after typing ends
              autoSuggestTimer = setTimeout(function(){
                doSearch();
              }, 1000);
            }
          }).bind('abort', function() {
            $(this).parent().find('ul.geoposition-results').remove();
          });

          ymaps.ready(function() {
            map = new ymaps.Map($mapContainer[0], mapOptions, {suppressMapOpenBlock: true});
            var typeSelector = new ymaps.control.TypeSelector(typeSelectorDefaults);
            map.controls.add(typeSelector);

            placemarkOptions = $.extend({}, placemarkDefaults, placemarkCustomOptions);

            if (!(latitude === null && longitude === null && placemarkOptions['geometry'])) {
              placemarkOptions['geometry'] = [latitude, longitude];
            }
            placemark = new ymaps.Placemark(
              placemarkOptions.geometry, placemarkOptions.properties, placemarkOptions.options
            );
            map.geoObjects.add(placemark);

            placemark.events.add("dragend", function(e) {
              var pos = e.originalEvent.target.geometry.getCoordinates();
              $latitudeField.val(pos[0]);
              $longitudeField.val(pos[1]);
              doGeocode();
            });

            if ($latitudeField.val() && $longitudeField.val()) {
              doGeocode();
            }

            $latitudeField.add($longitudeField).bind('keyup', function(e) {
              var latitude = parseFloat($latitudeField.val()) || 0;
              var longitude = parseFloat($longitudeField.val()) || 0;
              map.setCenter([latitude, longitude]);
              map.setZoom(15);
              placemark.geometry.setCoordinates([latitude, longitude]);
              doGeocode();
            });
          });
        }

        function showError() {
          var $err = $('<span/>', {'class': 'error'}).html('Error loading map');
          $container.append($err);
        }

        if (latitude && longitude) {
          $showMap.remove();
          $.getScript(mapUrl).done(showMap).fail(showError);
        } else {
          $showMap.click(function() {
            $.getScript(mapUrl).done(showMap).fail(showError);
            this.remove();
          });
        }

    });

  });

})(django.jQuery);
