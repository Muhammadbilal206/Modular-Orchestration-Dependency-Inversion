import csv
import json
from typing import Any

class CSVReader:
    def __init__(self, service_handler: Any):
        self.service = service_handler

    def read(self, filepath: str) -> None:
        raw_data = []
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    raw_data.append(row)
            
            if raw_data:
                print(f"CSV Columns detected: {list(raw_data[0].keys())}")
            
            print(f"CSVReader: Successfully read {len(raw_data)} rows from {filepath}.")
            self.service.execute(raw_data)

        except FileNotFoundError:
            print(f"Error: Could not find the CSV file at {filepath}")


class JSONReader:
    def __init__(self, service_handler: Any):
        self.service = service_handler

    def read(self, filepath: str) -> None:
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as file:
                raw_data = json.load(file)
            
            print(f"JSONReader: Successfully read data from {filepath}.")
            self.service.execute(raw_data)

        except FileNotFoundError:
            print(f"Error: Could not find the JSON file at {filepath}")
        except json.JSONDecodeError:
            print(f"Error: The file at {filepath} is not valid JSON.")
