import json
from plugins.inputs import CSVReader, JSONReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from core.engine import TransformationEngine

INPUT_DRIVERS = 
{
    "csv": CSVReader,
    "json": JSONReader
}

OUTPUT_DRIVERS = 
{
    "console": ConsoleWriter,
    "graphics": GraphicsChartWriter
}

def bootstrap():
    with open("config.json", "r") as file:
        config = json.load(file)

    input_choice = config["pipeline"]["input_source"] 
    output_choice = config["pipeline"]["output_sink"] 

    sink_class = OUTPUT_DRIVERS[output_choice]
    sink_instance = sink_class() 

    engine = TransformationEngine(sink=sink_instance, params=config["analysis_parameters"])

    input_class = INPUT_DRIVERS[input_choice]
    input_instance = input_class(service_handler=engine)

    input_instance.read(config["data"]["file_path"])

if __name__ == "__main__":
    bootstrap()
