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
            
            if not raw_data:
                print(f"Warning: The CSV file at {filepath} is empty.")
                return

            self.service.execute(raw_data)

        except FileNotFoundError:
            print(f"Error: Could not find the CSV file at {filepath}")
        except Exception as e:
            print(f"An unexpected error occurred reading CSV: {e}")


class JSONReader:
    def __init__(self, service_handler: Any):
        self.service = service_handler

    def read(self, filepath: str) -> None:
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as file:
                raw_data = json.load(file)
            
            if not isinstance(raw_data, list):
                print("Error: JSON data must be a list of objects to be processed by the Engine.")
                return

            print(f"JSONReader: Successfully read {len(raw_data)} records.")
            self.service.execute(raw_data)

        except FileNotFoundError:
            print(f"Error: Could not find the JSON file at {filepath}")
        except json.JSONDecodeError:
            print(f"Error: The file at {filepath} is not a valid JSON format.")
        except Exception as e:
            print(f"An unexpected error occurred reading JSON: {e}")
