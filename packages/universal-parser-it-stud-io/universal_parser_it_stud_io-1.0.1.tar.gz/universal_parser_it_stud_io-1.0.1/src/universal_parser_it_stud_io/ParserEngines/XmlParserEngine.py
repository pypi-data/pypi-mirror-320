import xml.etree.ElementTree as et
import xmlschema
from collections import defaultdict

class XmlParserEngine:
    def parse(self, data):
        root = et.fromstring(data)
        return self._parse_xml_element(root)
    
    def _parse_xml_element(self, element):
        parsed_data = {element.tag: {} if element.attrib else None}
        children = list(element)
        if children:
            dd = defaultdict(list)
            for dc in map(self._parse_xml_element, children):
                for k, v in dc.items():
                    dd[k].append(v)
            parsed_data = {element.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if element.attrib:
            parsed_data[element.tag].update(('@' + k, v) for k, v in element.attrib.items())
        if element.text:
            text = element.text.strip()
            if children or element.attrib:
                if text:
                    parsed_data[element.tag]['#text'] = text
            else:
                parsed_data[element.tag] = text
        return parsed_data
    
    def validate(self, data, schema):
        xml_schema = xmlschema.XMLSchema(schema)
        xml_schema.validate(data)
        return True