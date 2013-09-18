serializers
===========
Django compatible serializers

CursorJSON
-----------
Serialize data without model


###Registered
```
from django.core import serializers
serializers.register_serializer('cursorjson','serializers.cursorjson')
```

###Uses
Example serialize data from PostGIS
```
...
response = HttpResponse(content_type='application/json')
cursor = connections['osm'].cursor()
cursor.execute("SELECT id, name, ST_AsGeoJSON(ST_Transform(geom,4326)) AS geom FROM osm")
serializers.serialize('cursorjson', cursor, json=['geom'], stream=response)
...
```

###Params
json - list of fields which contains json object

primary - name for primary key (default "id"). If primary=None returns array of objects. If primary="id" then object {id:object,id:object..}



FeatureCollection
-------------
Serialize geofields from GeoQuerySet, list, tuple..

###Registered
```
from django.core import serializers
serializers.register_serializer('geojson','serializers.featurecollection')
```
or in settings.py:
```
SERIALIZATION_MODULES = { 'geojson' : 'serializers.featurecollection' }
```

###Uses
Example serialize data from geomodel
```
...
response = HttpResponse(content_type='application/json')
serializers.serialize('geojson', City.objects.all(), fields=['point','poly'], stream=response)
...
```

###Params
fields - list of geometry fields (for serialize geometry only)

geometry - geometry field into feature

geometry_collection - list of geometry fields (multigeometry for feature)

properties - list of fields (properties for feature)

