from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, authentication_classes


from .app import HiwatRapidViewer as app


import os
import json
import numpy as np
import netCDF4 as nc

from csv import writer as csv_writer

import datetime as dt
import plotly.graph_objs as go


base_name = __package__.split('.')[-1]


@login_required()
def home(request):

    geoserver_base_url = app.get_custom_setting('geoserver')
    geoserver_workspace = app.get_custom_setting('workspace')
    watershed = app.get_custom_setting('watershed')
    subbasin = app.get_custom_setting('subbasin')
    extra_feature = app.get_custom_setting('extra_feature')
    geoserver_endpoint = TextInput(display_text='',
                                   initial=json.dumps(
                                       [geoserver_base_url, geoserver_workspace, watershed, subbasin, extra_feature]),
                                   name='geoserver_endpoint',
                                   disabled=True)

    context = {
        'geoserver_endpoint': geoserver_endpoint
        }

    return render(request, 'hiwat_rapid_viewer/home.html', context)


def get_time_series(request):

    get_data = request.GET

    try:
        # model = get_data['model']
        watershed = get_data['watershed']
        subbasin = get_data['subbasin']
        comid = get_data['comid']
        units = 'metric'

        path = os.path.join(app.get_custom_setting(
            'hiwat_path'), '-'.join([watershed, subbasin]))
        filename = [f for f in os.listdir(path) if 'Qout' in f]
        res = nc.Dataset(os.path.join(app.get_custom_setting(
            'hiwat_path'), '-'.join([watershed, subbasin]), filename[0]), 'r')

        dates_raw = res.variables['time'][:]
        dates = []
        for d in dates_raw:
            dates.append(dt.datetime.fromtimestamp(d))

        comid_list = res.variables['rivid'][:]
        comid_index = int(np.where(comid_list == int(comid))[0])

        values = []
        for l in list(res.variables['Qout'][:]):
            values.append(float(l[comid_index]))

        # --------------------------------------
        # Chart Section
        # --------------------------------------
        series = go.Scatter(
            name='HIWAT',
            x=dates,
            y=values,
            )

        layout = go.Layout(
            title="HIWAT Streamflow<br><sub>{0} ({1}): {2}</sub>".format(
                watershed, subbasin, comid),
            xaxis=dict(
                title='Date',
                ),
            yaxis=dict(
                title='Streamflow ({}<sup>3</sup>/s)'
                      .format(get_units_title(units))
                )
            )

        chart_obj = PlotlyView(
            go.Figure(data=[series],
                      layout=layout)
            )

        context = {
            'gizmo_object': chart_obj,
            }

        return render(request, '{0}/gizmo_ajax.html'.format(base_name), context)

    except Exception as e:
        print str(e)
        return JsonResponse({'error': 'No HIWAT data found for the selected reach.'})


def get_units_title(unit_type):
    """
    Get the title for units
    """
    units_title = "m"
    if unit_type == 'english':
        units_title = "ft"
    return units_title


# @api_view(['GET'])
# @authentication_classes((TokenAuthentication, SessionAuthentication,))
def get_forecast_api(request):

    return_format = request.GET.get('return_format')
    get_info = request.GET
    watershed = get_info.get('watershed')
    subbasin = get_info.get('subbasin')
    river_id = get_info.get('river_id')

    if return_format == 'csv':
        try:

            path = os.path.join(app.get_custom_setting(
                'hiwat_path'), '-'.join([watershed, subbasin]))

            if not os.path.exists(path):
                return JsonResponse({'error': "Location of forecast files faulty.Please check Config."})

            filename = [f for f in os.listdir(path) if 'Qout' in f]
            res = nc.Dataset(os.path.join(app.get_custom_setting(
                'hiwat_path'), '-'.join([watershed, subbasin]), filename[0]), 'r')

            dates_raw = res.variables['time'][:]
            dates = []
            for d in dates_raw:
                dates.append(dt.datetime.fromtimestamp(d))

            comid_list = res.variables['rivid'][:]
            comid_index = int(np.where(comid_list == int(river_id))[0])

            values = []
            for l in list(res.variables['Qout'][:]):
                values.append(float(l[comid_index]))

        except ValueError as err:
            print str(err)
            return JsonResponse({'error': str(err)})

        # prepare to write response for CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename=forecasted_streamflow_{0}_{1}_{2}.csv' \
            .format(watershed,
                    subbasin,
                    river_id)

        writer = csv_writer(response)

        writer.writerow(['datetime', 'Flow'])

        finalData = zip(dates, values)

        for row_data in finalData:
            writer.writerow(row_data)

        return response
    else:
        raise InvalidData('Only CSV format supported as of now. ')
