from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text
from django.db.models import Lookup
from django.db.models.lookups import PatternLookup

from . import Geoposition
from .forms import GeopositionField as GeopositionFormField
from .geohash import geo_expand


class GeopositionField(models.Field):
    description = _("A geoposition (latitude and longitude)")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 52
        super(GeopositionField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        if not value or value == 'None':
            return None
        if isinstance(value, Geoposition):
            return value
        if isinstance(value, list):
            return Geoposition(value[1], value[2], value[0]) if len(value) == 3 else Geoposition(value[0], value[1])

        # default case is string
        value_parts = value.rsplit(',')

        geohash = value_parts[0] if len(value_parts) == 3 else None

        try:
            latitude = value_parts[1 if len(value_parts) == 3 else 0]
        except IndexError:
            latitude = '0.0'
        try:
            longitude = value_parts[2 if len(value_parts) == 3 else 1]
        except IndexError:
            longitude = '0.0'

        return Geoposition(latitude, longitude, geohash)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def get_prep_value(self, value):
        if isinstance(value, Geoposition):
            value.rehash()
            return ",".join(
                [value.geohash, str(value.latitude), str(value.longitude)]
            )
        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return smart_text(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': GeopositionFormField
        }
        defaults.update(kwargs)
        return super(GeopositionField, self).formfield(**defaults)


@GeopositionField.register_lookup
class GeoSearchMatchedLookup(Lookup):
    lookup_name = 'geosearch'

    def __init__(self, lhs, rhs):
        super(GeoSearchMatchedLookup, self).__init__(lhs, rhs)

    def process_rhs(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = super(GeoSearchMatchedLookup, self).process_rhs(compiler, connection)
        rhs = ''
        params = rhs_params[0]
        if params and not self.bilateral_transforms:
            rhs_params = geo_expand(params)
            rhs_params_count = len(rhs_params)
            if rhs_params_count:
                rhs += '('
            for i in range(0, rhs_params_count):
                rhs_params[i] = "%s%%" % connection.ops.prep_for_like_query(rhs_params[i])
                if i < rhs_params_count - 1:
                    rhs += lhs + ' like %s OR '
                else:
                    rhs += lhs + 'like %s)'
        return rhs, rhs_params

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return rhs, params


@GeopositionField.register_lookup
class GeoPreciseSearchMatchedLookup(PatternLookup):
    lookup_name = 'geoprecise'

    def __init__(self, lhs, rhs):
        super(GeoPreciseSearchMatchedLookup, self).__init__(lhs, rhs)

    def get_rhs_op(self, connection, rhs):
        return connection.operators['startswith'] % rhs

    def process_rhs(self, qn, connection):
        rhs, params = super(GeoPreciseSearchMatchedLookup, self).process_rhs(qn, connection)
        if params and not self.bilateral_transforms:
            params[0] = "%s%%" % connection.ops.prep_for_like_query(params[0])
        return rhs, params
