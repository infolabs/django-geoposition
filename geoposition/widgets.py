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
        if isinstance(value, list):
            return value
        if isinstance(value, six.text_type):
            return value.rsplit(',')
        if value:
            return [value.latitude, value.longitude]
        return [None, None]

    def format_output(self, rendered_widgets):
        if settings.WIDGET == 'yandex':
            map_url = 'https://api-maps.yandex.ru/2.1/?apikey=%s&lang=%s' % (settings.YANDEX_MAPS_API_KEY,
                                                                             settings.YANDEX_MAPS_LANG)
        else:
            map_url = 'https://maps.google.com/maps/api/js?key=%s&language=%s' % (settings.GOOGLE_MAPS_API_KEY,
                                                                                  settings.GOOGLE_MAPS_LANG)
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
                'map_url': map_url,
            }
        })

    def render(self, name, value, attrs=None, renderer=None):
        value = self.decompress(value)
        rendered_widgets = []
        for i, widget in enumerate(self.widgets):
            rendered_widgets.append(widget.render('{}_{}'.format(name, i), value[i], {'class': name}))
        return self.format_output(rendered_widgets)


class YandexGeopositionWidget(BaseGeopositionWidget):
    def __init__(self, attrs=None):
        super(YandexGeopositionWidget, self).__init__(attrs=attrs)

    class Media:
        js = (
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
            'geoposition/geoposition.js',
        )
        css = {
            'all': ('geoposition/geoposition.css',)
        }
