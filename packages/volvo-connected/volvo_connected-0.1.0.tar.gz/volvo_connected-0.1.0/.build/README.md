# Volvo API specs

The specs can be downloaded at: `https://developer.volvocars.com/apis/connected-vehicle/v2/specification/`

## Generate the API

The VolvoClient is generated using [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/overview)

```ps1
# Install Kiota
dotnet tool install microsoft.openapi.kiota -g

kiota generate -d ./.build/volvo_connected_specs.json -o ./src/volvo_connected/vcclient -l Python -c VolvoConnectedClient --ebc --serializer kiota_serialization_json.json_serialization_writer_factory.JsonSerializationWriterFactory --deserializer kiota_serialization_json.json_parse_node_factory.JsonParseNodeFactory --co
```