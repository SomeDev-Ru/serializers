
import six
# import json


class Serializer(object):
    
    def serialize(self, cursor, **options):
        """
        Serialize a cursor.
        """
        self.options = options
        self.cols = [col.name for col in cursor.description]

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.json_keys = options.pop("json", None)
        self.primary = options.pop("primary", 'id')
        self.use_natural_keys = options.pop("use_natural_keys", False)

        self.start_serialization()
        self.first = True
        for obj in cursor:
            self.start_object(obj)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
#         if json.__version__.split('.') >= ['2', '1', '3']:
#             # Use JS strings to represent Python Decimal instances (ticket #16850)
#             self.options.update({'use_decimal': False})
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        if self.primary is None:
            self.stream.write("[")
        else:
            self.stream.write("{")

    def gen_kv(self, obj):
        self.first = True
        first = 0 if self.primary is None else 1
        try:
            for i in range(len(self.cols)):
                yield (self.cols[first+i],obj[first+i])
                self.first = False
        except IndexError:
            yield None

    def start_object(self, obj):
        pass

    def end_object(self, obj):
        if not self.first:
            self.stream.write(",")
        if self.primary is None:
            self.stream.write('{')
        else:
            self.stream.write('"%i":{' % obj[0])
        for i in self.gen_kv(obj):
            if i is None:
                break
            else:
                if not self.first:
                    self.stream.write(",")
            if i[1] is None:
                self.stream.write('"%s":null' % i[0])
            elif i[0] in self.json_keys:
                self.stream.write('"%s":%s' % i)
            else:
                self.stream.write('"%s":"%s"' % i)
        self.stream.write('}')
        self._current = None

    def end_serialization(self):
        if self.primary is None:
            self.stream.write("]")
        else:
            self.stream.write("}")

    def getvalue(self):
        pass
