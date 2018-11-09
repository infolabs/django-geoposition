from __future__ import unicode_literals

import json

from django import forms
from django.template.loader import render_to_string
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from .conf import settings


class BaseGeopositionWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(),
            forms.TextInput(),
        )
        super(BaseGeopositionWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, six.text_type):
            return value.rsplit(',')
        if value:
            return [value.latitude, value.longitude]
        return [None, None]

    def format_output(self, rendered_widgets):
        return render_to_string('geoposition/widgets/geoposition.html', {
            'latitude': {
                'html': rendered_widgets[0],
                'label': _("latitude"),
            },
            'longitude': {
                'html': rendered_widgets[1],
                'label': _("longitude"),
            },
            'config': {
                'map_widget_height': settings.MAP_WIDGET_HEIGHT or 500,
                'map_options': json.dumps(settings.MAP_OPTIONS),
                'marker_options': json.dumps(settings.MARKER_OPTIONS),
            }
        })


class YandexGeopositionWidget(BaseGeopositionWidget):
    def __init__(self, attrs=None):
        super(YandexGeopositionWidget, self).__init__(attrs=attrs)

    class Media:
        js = (
            '//api-maps.yandex.ru/2.1/?lang=%s' % settings.YANDEX_MAPS_LANG,
            'geoposition/geoposition_yandex.js',
        )
        css = {
            'all': ('geoposition/geoposition.css',)
        }


class GoogleGeopositionWidget(BaseGeopositionWidget):
    def __init__(self, attrs=None):
        super(GoogleGeopositionWidget, self).__init__(attrs=attrs)

    class Media:
        js = (
            '//maps.google.com/maps/api/js?key=%s' % settings.GOOGLE_MAPS_API_KEY,
            'geoposition/geoposition.js',
        )
        css = {
            'all': ('geoposition/geoposition.css',)
        }
