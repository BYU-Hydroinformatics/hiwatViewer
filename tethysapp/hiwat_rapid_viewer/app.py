from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class HiwatRapidViewer(TethysAppBase):

    name = 'HIWAT Rapid Viewer'
    index = 'hiwat_rapid_viewer:home'
    icon = 'hiwat_rapid_viewer/images/icon.gif'
    package = 'hiwat_rapid_viewer'
    root_url = 'hiwat-rapid-viewer'
    color = '#c0392b'
    description = 'Place a brief description of your app here.'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='hiwat-rapid-viewer',
                controller='hiwat_rapid_viewer.controllers.home'
                ),
            UrlMap(
                name='get-time-series',
                url='get-time-series',
                controller='hiwat_rapid_viewer.controllers.get_time_series'
                ),
            # API DECLARATIONS
            UrlMap(name='waterml',
                   url='hiwat-rapid-viewer/api/GetForecast',
                   controller='hiwat_rapid_viewer.controllers.get_forecast_api'),
            )

        return url_maps

    def custom_settings(self):
        return (
            CustomSetting(
                name='geoserver',
                type=CustomSetting.TYPE_STRING,
                description='Spatial dataset service for app to use',
                required=True
                ),
            CustomSetting(
                name='workspace',
                type=CustomSetting.TYPE_STRING,
                description='Workspace within Geoserver where web service is',
                required=True
                ),
            CustomSetting(
                name='watershed',
                type=CustomSetting.TYPE_STRING,
                description='Watershed Name ( eg. nepal)',
                required=True
                ),
            CustomSetting(
                name='subbasin',
                type=CustomSetting.TYPE_STRING,
                description='SubBasin Name ( eg. national)',
                required=True
                ),
            CustomSetting(
                name='extra_feature',
                type=CustomSetting.TYPE_STRING,
                description='Name of an additional feature to load from  the provided geoserver (e.g. a boundary layer).',
                required=False,
                ),
            CustomSetting(
                name='hiwat_path',
                type=CustomSetting.TYPE_STRING,
                description='Path to local HIWAT-RAPID directory',
                required=False
                ),
            )
