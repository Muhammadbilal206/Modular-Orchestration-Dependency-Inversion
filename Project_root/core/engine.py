from typing import List, Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__(self, sink: DataSink, params: dict):
        self.sink = sink [cite: 85]
        self.params = params

    def execute(self, raw_data: List[Any]) -> None:
        print("Engine received data. Starting transformations...")

        target_continent = self.params.get("target_continent")
        target_year = self.params.get("target_year")
        processed_results = raw_data 
        self.sink.write(processed_results)
