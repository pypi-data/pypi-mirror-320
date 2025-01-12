# universal-parser
An universal parser for various file formats.

## usage
This package can be used to parse and validate data from various file formats like JSON, XML, CSV, YAML.

### install univeral-parser package
```pip install -r universal-parser-it-stud-io```

### create app.py file
``` 
json_data = '{"name": "John", "age": 30}'
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

xml_data = '<person><name>John</name><age>30</age></person>'
xml_schema = '''
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="person">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="age" type="xs:integer"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
'''

csv_data = 'name,age\nJohn,30'
csv_schema = {
    "name": str,
    "age": int
}

yaml_data = '''
name: John
age: 30
'''
yaml_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

from universal_parser_it_stud_io import UniversalParser

parser = UniversalParser.UniversalParser(json_data)
print("Detected format: ", parser._data_format)
print(parser.parse())
print(parser.validate(json_schema))

parser = UniversalParser.UniversalParser(xml_data)
print("Detected format: ", parser._data_format)
print(parser.parse())
print(parser.validate(xml_schema))

parser = UniversalParser.UniversalParser(csv_data)
print("Detected format: ", parser._data_format)
print(parser.parse())
print(parser.validate(csv_schema))

parser = UniversalParser.UniversalParser(yaml_data)
print("Detected format: ", parser._data_format)
print(parser.parse())
print(parser.validate(yaml_schema))
```

### run app.py
```python app.py```