
import json
try:
    from django.core.serializers.json import DjangoJSONEncoder as JSONEncoder
    from django.utils import six
except ImportError:
    import six
    JSONEncoder = json.JSONEncoder


class Serializer(object):
    
    internal_use_only = False
    
    @staticmethod
    def hasattr2(s,attr):
        if isinstance(s, dict):
            return s.has_key(attr)
        return hasattr(s,attr)
    
    @staticmethod
    def getattr2(s,attr):
        if isinstance(s, dict):
            return s[attr]
        return getattr(s,attr)
    
    def serialize(self, queryset, **options):
        self.options = options
        self.properties = self.options.pop('properties', ())
        self.kv = self.options.pop('kv', {})
        self.geometry_collection = self.options.pop('geometry_collection', ())
        if len(self.geometry_collection) == 0: 
            self.geometry_collection = self.options.pop('geometry_collections', ()) # Deprecated
        self.geometry = self.options.pop('geometry', None)
        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", ())
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        self.stream.write('{"type":"FeatureCollection","features":[')

    def start_object(self, obj):
        self._current = obj

    def end_object(self, obj):
        for field in self.selected_fields:
            geom = getattr(obj, field)
            if geom is not None:
                if not self.first:
                    self.stream.write(",")
                self.stream.write(geom.geojson)
                self.first = False
        if self.geometry is None and len(self.geometry_collection) == 0 and len(self.properties) == 0:
            return
        if not self.first:
            self.stream.write(",")
        self.stream.write('{"type":"Feature",')
        self.first = True
        self.rend_geometry()
        self.rend_prop()
        self.stream.write("}")
        self._current = None
    
    def rend_prop(self):
        if len(self.properties) == 0:
            return
        if not self.first:
            self.stream.write(",")
        self.stream.write('"properties":{')
        self.first = True
        for prop in self.properties:
            if self.hasattr2(self._current, prop):
                if not self.first:
                    self.stream.write(",")
                self.stream.write('"%s":' % (prop,))
                json.dump(self.getattr2(self._current, prop), self.stream,
                      cls=Encoder, **self.json_kwargs)
                self.first = False
        self.first = False
        self.stream.write("}")
    
    def rend_geometry(self):
        if self.geometry is not None or len(self.geometry_collection) != 0:
            if not self.first:
                self.stream.write(",")
            self.stream.write('"geometry":')
        else:
            return
        if self.geometry is not None:
            geom = getattr(self._current, self.geometry)
            if geom is not None:
                self.stream.write(geom.geojson)
            else:
                self.stream.write('null')
            self.first = False
            return
        if len(self.geometry_collection) == 0:
            return
        self.stream.write('{"type":"GeometryCollection","geometries":[')
        self.first = True
        for geom in self.geometry_collection:
            geom = getattr(self._current, geom)
            if geom is not None:
                if not self.first:
                    self.stream.write(",")
                self.stream.write(geom.geojson)
                self.first = False
        self.first = False
        self.stream.write("]}")
        

    def end_serialization(self):
        self.stream.write("]")
        for k, v in self.kv.items():
            if not self.first:
                self.stream.write(",")
            self.stream.write('"%s":%s' % (k, json.dumps(v)))
            self.first = False
        self.stream.write("}")

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return str(o)
        elif callable(getattr(o, '__unicode__', getattr(o, '__str__', None))):
            return getattr(o, '__unicode__', getattr(o, '__str__', None))()
        else:
            return super(Encoder, self).default(o)
