
from django.core.serializers.json import Serializer as jsonSerializer, Deserializer
import json

class Serializer(jsonSerializer):

    def start_serialization(self):
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        self.stream.write('{"type":"FeatureCollection","features":[')

    def end_object(self, obj):
        for field in self.selected_fields:
            if not self.first:
                self.stream.write(",")
            self.stream.write(getattr(obj,field).json)
            self.first = False
        self._current = None

    def end_serialization(self):
        for k,v in self.options.pop('kv',{}).items():
            if not self.first:
                self.stream.write(",")
            self.stream.write('"%s":%s' % (k,json.dumps(v)))
            self.first = False
        self.stream.write("]}")
