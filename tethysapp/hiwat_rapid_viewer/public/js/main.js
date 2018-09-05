// Hide stuff not needed

$('#app-content-wrapper').removeClass('show-nav')
$('.toggle-nav').removeClass('toggle-nav')

const geoserverURL = `http://tethys-staging.byu.edu:8181/geoserver/wms`

var projection = ol.proj.get('EPSG:3857')
var baseLayer = new ol.layer.Tile({
    source: new ol.source.BingMaps({
        key:
            '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
        imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
    })
})
var fullScreenControl = new ol.control.FullScreen()
var view = new ol.View({
    center: ol.proj.transform([90.3, 23.6], 'EPSG:4326', 'EPSG:3857'),
    projection: projection,
    zoom: 5
})

var default_style = new ol.style.Style({
    fill: new ol.style.Fill({
        color: [250, 250, 250, 0.1]
    }),
    stroke: new ol.style.Stroke({
        color: [220, 220, 220, 1],
        width: 4
    })
})

select_source = new ol.source.Vector()

select_layer = new ol.layer.Vector({
    name: 'select_layer',
    source: select_source,
    style: default_style
})

districtLayer = new ol.layer.Tile({
    name: 'districts',
    source: new ol.source.TileWMS({
        crossOrigin: 'anonymous', // // KS Refactor Design 2016 Override // This should enable screenshot export around the CORS issue with Canvas.
        url: geoserverURL,
        params: {
            LAYERS: 'utils:adminOne',
            TILED: true
        },
        serverType: 'geoserver'
    })
})

var workspace = JSON.parse($('#geoserver_endpoint').val())[1]
var model = $('#model option:selected').text()
var watershed = JSON.parse($('#geoserver_endpoint').val())[2]
var subbasin = JSON.parse($('#geoserver_endpoint').val())[3]

var layerName = workspace + ':' + watershed + '-' + subbasin + '-drainage_line'

wmsLayer = new ol.layer.Image({
    source: new ol.source.ImageWMS({
        url:
            JSON.parse($('#geoserver_endpoint').val())[0].replace(/\/$/, '') +
            '/wms',
        params: { LAYERS: layerName },
        serverType: 'geoserver',
        crossOrigin: 'Anonymous'
    })
})

layers = [baseLayer, districtLayer, select_layer, wmsLayer]

map = new ol.Map({
    target: document.getElementById('map'),
    layers: layers,
    view: view
})

map.on('pointermove', function(evt) {
    if (evt.dragging) {
        return
    }
    var model = $('#model option:selected').text()
    var pixel = map.getEventPixel(evt.originalEvent)

    var hit = map.forEachLayerAtPixel(pixel, function(layer) {
        if (layer == wmsLayer) {
            current_layer = layer
            return true
        }
    })

    map.getTargetElement().style.cursor = hit ? 'pointer' : ''
})

map.on('singleclick', function(evt) {
    if (map.getTargetElement().style.cursor == 'pointer') {
        $('#sf-plot-modal').modal('show')
        var view = map.getView()
        var viewResolution = view.getResolution()

        var wms_url = current_layer
            .getSource()
            .getGetFeatureInfoUrl(
                evt.coordinate,
                viewResolution,
                view.getProjection(),
                { INFO_FORMAT: 'application/json' }
            ) //Get the wms url for the clicked point

        if (wms_url) {
            $('#loading-forecast').removeClass('hidden')

            $.ajax({
                type: 'GET',
                url: wms_url,
                dataType: 'json',
                success: function(result) {
                    let comid = result['features'][0]['properties']['COMID']

                    get_time_series(model, watershed, subbasin, comid)
                },
                error: function(error) {
                    console.log(error)
                }
            })
        }
    }
})

function get_time_series(model, watershed, subbasin, comid) {
    $('#loading-forecast').removeClass('hidden')
    $('#forecastChart').addClass('hidden')
    $.ajax({
        type: 'GET',
        url: 'get-time-series/',
        data: {
            model: model,
            watershed: watershed,
            subbasin: subbasin,
            comid: comid
        },
        error: function() {
            $('#info').html(
                '<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the forecast</strong></p>'
            )
            $('#info').removeClass('hidden')

            setTimeout(function() {
                $('#info').addClass('hidden')
            }, 5000)
        },
        success: function(data) {
            if (!data.error) {
                $('#loading-forecast').addClass('hidden')
                $('#forecastChart').removeClass('hidden')
                $('#forecastChart').html(data)

                //resize main graph
                Plotly.Plots.resize($('#forecastChart .js-plotly-plot')[0])

                var params = {
                    watershed_name: watershed,
                    subbasin_name: subbasin,
                    reach_id: comid
                }

                // $('#submit-download-forecast').attr({
                //     target: '_blank',
                //     href: 'get-forecast-data-csv?' + jQuery.param(params)
                // })

                // $('#download_forecast').removeClass('hidden')
            } else if (data.error) {
                $('#info').html(
                    '<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the forecast</strong></p>'
                )
                $('#info').removeClass('hidden')

                setTimeout(function() {
                    $('#info').addClass('hidden')
                }, 5000)
            } else {
                $('#info')
                    .html(
                        '<p><strong>An unexplainable error occurred.</strong></p>'
                    )
                    .removeClass('hidden')
            }
        }
    })
}
