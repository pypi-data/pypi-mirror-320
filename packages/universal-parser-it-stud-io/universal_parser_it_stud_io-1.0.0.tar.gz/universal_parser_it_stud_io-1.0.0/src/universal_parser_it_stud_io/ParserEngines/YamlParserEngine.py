import yaml

class YamlParserEngine:
    def parse(self, data):
        return yaml.safe_load(data)
    
    def validate(self,  data, schema):
        yaml_data = yaml.safe_load(data)
        # Implement your YAML validation logic here
        return True