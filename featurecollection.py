
try:
    from django.core.serializers.json import DjangoJSONEncoder as Encoder
    from django.utils import six
except:
    import six
    Encoder = json.JSONEncoder
import json


class Serializer(object):
    
    def serialize(self, queryset, **options):
        self.options = options
        self.properties = self.options.pop('properties', ())
        self.kv = self.options.pop('kv',{})
        self.geometry_collections = self.options.pop('geometry_collections', ())
        self.geometry = self.options.pop('geometry', None)

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            self.end_object(obj)
            if self.first:
                self.first = False
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
            if not self.first:
                self.stream.write(",")
            self.stream.write(getattr(obj,field).geojson)
            self.first = False
        if self.geometry is None and len(self.geometry_collections)==0:
            return
        if not self.first:
            self.stream.write(",")
        self.stream.write('{"type": "Feature",')
        self.first = True
        self.rend_geometry()
        self.rend_prop()
        self.stream.write("}")
        self._current = None
    
    def rend_prop(self):
        if not self.first:
            self.stream.write(",")
        self.stream.write('"properties":{')
        self.first = True
        for prop in self.properties:
            if not self.first:
                self.stream.write(",")
            self.stream.write('"%s":' % (prop,))
            json.dump(getattr(self._current,prop), self.stream,
                  cls=Encoder, **self.json_kwargs)
            self.first = False
        self.first = False
        self.stream.write("}")
    
    def rend_geometry(self):
        if not self.first:
            self.stream.write(",")
        self.stream.write('"geometry":')
        if self.geometry is not None:
            self.stream.write(getattr(self._current,self.geometry).geojson)
            self.first = False
            return
        self.stream.write('{"type":"GeometryCollection","geometries":[')
        self.first = True
        for geom in self.geometry_collections:
            if not self.first:
                self.stream.write(",")
            self.stream.write(getattr(self._current,geom).geojson)
            self.first = False
        self.first = False
        self.stream.write("]}")
        

    def end_serialization(self):
        self.stream.write("]")
        for k,v in self.kv.items():
            if not self.first:
                self.stream.write(",")
            self.stream.write('"%s":%s' % (k,json.dumps(v)))
            self.first = False
        self.stream.write("}")

    def getvalue(self):
        pass
