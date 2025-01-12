import json
import csv
import yaml
import xml.etree.ElementTree as et
from .ParserEngines.JsonParserEngine import JsonParserEngine
from .ParserEngines.XmlParserEngine import XmlParserEngine
from .ParserEngines.CsvParserEngine import CsvParserEngine
from .ParserEngines.YamlParserEngine import YamlParserEngine

class UniversalParser:
    def __init__(self, data=None):
        self._data = data
        self._data_format = self._detect_format()
        self._parser_engine = self._get_parser_engine()

    def parse(self):
        return self._parser_engine.parse(self._data)

    def validate(self, schema):
        return self._parser_engine.validate(self._data, schema)
        
    def _detect_format(self):
        try:
            json.loads(self._data)
            return 'json'
        except json.JSONDecodeError:
            pass
        try:
            et.fromstring(self._data)
            return 'xml'
        except et.ParseError:
            pass
        try:
            csv.Sniffer().sniff(self._data, delimiters=',')
            return 'csv'
        except csv.Error:
            pass
        try:
            yaml.safe_load(self._data)
            return 'yaml'
        except yaml.YAMLError:
            pass
        raise ValueError("Unable to detect data format")
    
    def _get_parser_engine(self):
        if self._data_format == 'json':
            return JsonParserEngine()
        elif self._data_format == 'xml':
            return XmlParserEngine()
        elif self._data_format == 'csv':
            return CsvParserEngine()
        elif self._data_format == 'yaml':
            return YamlParserEngine()
        else:
            raise ValueError("Unsupported data format")