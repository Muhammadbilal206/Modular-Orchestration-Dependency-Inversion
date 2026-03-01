import json
import os
import sys
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from core.engine import TransformationEngine

INPUT_DRIVERS = {
    "csv": CSVReader,
    "json": JSONReader
}

OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "graphics": GraphicsChartWriter
}

def bootstrap():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file missing at {config_path}")

        with open(config_path, "r") as file:
            config = json.load(file)

        pipeline = config.get("pipeline", {})
        input_choice = pipeline.get("input_source")
        output_choice = pipeline.get("output_sink")

        if input_choice not in INPUT_DRIVERS:
            raise ValueError(f"Invalid input_source '{input_choice}'. Valid options: {list(INPUT_DRIVERS.keys())}")
        
        if output_choice not in OUTPUT_DRIVERS:
            raise ValueError(f"Invalid output_sink '{output_choice}'. Valid options: {list(OUTPUT_DRIVERS.keys())}")

        params = config.get("analysis_parameters", {})
        data_config = config.get("data", {})
        file_path = data_config.get("file_path")

        if not file_path:
            raise ValueError("Missing 'file_path' in 'data' configuration block.")

        sink_instance = OUTPUT_DRIVERS[output_choice]()
        engine = TransformationEngine(sink=sink_instance, params=params)
        
        input_instance = INPUT_DRIVERS[input_choice](service_handler=engine)
        data_path = os.path.join(base_dir, file_path)
        
        input_instance.read(data_path)

    except json.JSONDecodeError:
        print("Critical Error: config.json is not a valid JSON file. Check for missing quotes or commas.")
        sys.exit(1)
    except Exception as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
