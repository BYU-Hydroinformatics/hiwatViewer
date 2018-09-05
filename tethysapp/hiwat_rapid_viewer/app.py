from tethys_sdk.base import TethysAppBase, url_map_maker


class HiwatRapidViewer(TethysAppBase):
    """
    Tethys app class for HIWAT Rapid Viewer.
    """

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
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='hiwat-rapid-viewer',
                controller='hiwat_rapid_viewer.controllers.home'
            ),
        )

        return url_maps
