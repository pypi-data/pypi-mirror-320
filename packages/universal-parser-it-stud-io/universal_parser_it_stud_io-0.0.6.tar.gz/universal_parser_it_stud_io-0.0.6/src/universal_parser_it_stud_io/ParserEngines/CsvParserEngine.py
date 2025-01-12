import csv

class CsvParserEngine:
    def parse(self, data):
        reader = csv.DictReader(data.splitlines())
        return [row for row in reader]
    
    def validate(self, data, schema):
        reader = csv.DictReader(data.splitlines())
        for row in reader:
            for field, field_type in schema.items():
                if field not in row:
                    raise ValueError(f"Missing field: {field}")
                try:
                    row[field] = field_type(row[field])
                except ValueError:
                    raise ValueError(f"Incorrect type for field: {field}")
        return True