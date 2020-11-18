from __future__ import unicode_literals

import requests
from .conf import settings

YANDEX_KIND = 'house'
YANDEX_FORMAT = 'json'


def forward_geocode_yandex(address):
    tpl = "https://geocode-maps.yandex.ru/1.x/?geocode={geocode}&apikey={apikey}&kind={kind}&format={fmt}&lang={lang}"
    url = tpl.format(geocode=address,
                     apikey=settings.YANDEX_MAPS_API_KEY,
                     kind=YANDEX_KIND,
                     fmt=YANDEX_FORMAT,
                     lang=settings.YANDEX_MAPS_LANG)

    r = requests.get(url, headers={'User-Agent': "curl/7.38.0"})
    r.raise_for_status()

    geocollection = r.json()['response']['GeoObjectCollection']['featureMember']
    results = []
    for g in geocollection:
        address = g['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']
        point = g['GeoObject']['Point']
        results.append({
            'text': address['formatted'],
            'postal_code': address.get('postal_code', None),
            'geoposition': point['pos']
        })

    return results


def forward_geocode(address):
    if settings.WIDGET == 'yandex':
        return forward_geocode_yandex(address)
    else:
        raise NotImplementedError
