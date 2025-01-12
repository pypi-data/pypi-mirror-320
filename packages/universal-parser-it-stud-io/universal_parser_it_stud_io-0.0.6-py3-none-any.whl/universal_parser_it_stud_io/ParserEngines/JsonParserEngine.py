import json
import jsonschema

class JsonParserEngine:
    def parse(self, data):
        return json.loads(data)
    
    def validate(self, data, schema):
        json_data = json.loads(data)
        jsonschema.validate(instance=json_data, schema=schema)
        return True