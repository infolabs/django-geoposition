# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured


class AppSettings(object):
    defaults = {
        'MAP_WIDGET_HEIGHT': 480,
        'MAP_OPTIONS': {},
        'MARKER_OPTIONS': {},
        'GOOGLE_MAPS_API_KEY': None,
        'YANDEX_MAPS_API_KEY': None,
        'YANDEX_MAPS_LANG': 'ru_RU',
        'GOOGLE_MAPS_LANG': 'ru',
        'WIDGET': 'yandex'
    }
    prefix = 'GEOPOSITION'

    def __init__(self, django_settings):
        self.django_settings = django_settings
        if self.django_settings.GEOPOSITION_WIDGET == 'google':
            self.check_setting('GOOGLE_MAPS_API_KEY')
        if self.django_settings.GEOPOSITION_WIDGET == 'yandex':
            self.check_setting('YANDEX_MAPS_API_KEY')

    def __getattr__(self, name):
        prefixed_name = '%s_%s' % (self.prefix, name)
        if hasattr(django_settings, prefixed_name):
            return getattr(django_settings, prefixed_name)
        if name in self.defaults:
            return self.defaults[name]
        raise AttributeError("'AppSettings' object does not have a '%s' attribute" % name)

    def check_setting(self, setting):
        prefixed_name = '%s_%s' % (self.prefix, setting)
        if not hasattr(self.django_settings, prefixed_name):
            raise ImproperlyConfigured("The '%s' setting is required." % prefixed_name)


settings = AppSettings(django_settings)
