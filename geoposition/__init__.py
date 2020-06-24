from __future__ import unicode_literals
from decimal import Decimal
from .geohash import geo_encode


default_app_config = 'geoposition.apps.GeoPositionConfig'

VERSION = (0, 3, 0)
__version__ = '.'.join(map(str, VERSION))

GEOHASH_PRECISION = 9


class Geoposition(object):
    def __init__(self, latitude, longitude, geohash=None):
        if isinstance(latitude, float) or isinstance(latitude, int):
            latitude = str(latitude)
        if isinstance(longitude, float) or isinstance(longitude, int):
            longitude = str(longitude)

        self.latitude = Decimal(latitude)
        self.longitude = Decimal(longitude)

        if geohash is None:
            self.rehash()
        else:
            self.geohash = geohash

    def __str__(self):
        return "%s,%s" % (self.latitude, self.longitude)

    def __repr__(self):
        return "<Geoposition %s>" % str(self)

    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        return isinstance(other, Geoposition) and self.latitude == other.latitude and self.longitude == other.longitude

    def __ne__(self, other):
        return not isinstance(other, Geoposition) or self.latitude != other.latitude or self.longitude != other.longitude

    def __gt__(self, other):
        return not isinstance(other, Geoposition) or self.geohash > other.geohash

    def __lt__(self, other):
        return not isinstance(other, Geoposition) or self.geohash < other.geohash

    def rehash(self):
        self.geohash = geo_encode(
            float(self.latitude), float(self.longitude), GEOHASH_PRECISION
        )


def str_to_geoposition(value):
    """
    Create Geoposition from string (format: r'^\d+(?:\.\d+)?,\d+(?:\.\d+)?$')
    :param value:
    :return:
    """
    value = value.split(',')
    for i in range(len(value)):
        value[i] = float(value[i])
    return Geoposition(*value)
