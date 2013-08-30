serializers
===========
Django compatible serializers

CursorJSON
-----------
Serialize data without model


###Registered
`serializers.register_serializer('cursorjson','serializers.cursorjson')`

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
json - list of fields wich contains json object
