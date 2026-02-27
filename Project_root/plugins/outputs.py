import matplotlib.pyplot as plt
from typing import List

class ConsoleWriter:
    def write(self, records: List[dict]) -> None:
        print("\n--- GDP Analysis Results ---")
        if not records:
            print("No data available to print.")
            return
            
        for record in records:
            print(record)
        print("----------------------------\n")


class GraphicsChartWriter:
    def write(self, records: List[dict]) -> None:
        print("GraphicsChartWriter: Generating charts...")
        
        if not records:
            print("No data available to plot.")
            return

        countries = list(map(lambda x: x.get('Country', 'Unknown'), records))
        gdp_values = list(map(lambda x: x.get('GDP', 0), records))


        plt.figure(figsize=(10, 6))
        plt.bar(countries, gdp_values, color='skyblue')
        

        plt.xlabel('Country')
        plt.ylabel('GDP')
        plt.title('GDP Analysis Output')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        

        plt.show()
