from typing import List, Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__(self, sink: DataSink, params: dict):
        self.sink = sink
        self.params = params

    def execute(self, raw_data: List[Any]) -> None:
        target_continent = self.params.get("target_continent")
        target_year = str(self.params.get("target_year"))
        end_year = int(self.params.get("end_year"))
        decline_years = int(self.params.get("decline_years"))

        def get_gdp(row, year):
            try:
                return float(row.get(str(year), 0))
            except (ValueError, TypeError):
                return 0.0

        continent_data = list(filter(lambda r: r.get('Continent') == target_continent, raw_data))

        mapped_gdp = list(map(lambda r: {"Country": r.get("Country", "Unknown"), "GDP": get_gdp(r, target_year)}, continent_data))
        valid_gdp = list(filter(lambda x: x["GDP"] > 0, mapped_gdp))
        
        top_10 = sorted(valid_gdp, key=lambda x: x["GDP"], reverse=True)[:10]

        def check_decline(row):
            years = [end_year - i for i in range(decline_years + 1)]
            gdps = [get_gdp(row, y) for y in years]
            if 0.0 in gdps:
                return False
            declines = list(map(lambda i: gdps[i] < gdps[i+1], range(len(gdps)-1)))
            return all(declines) and len(declines) > 0

        declining_countries = list(map(lambda r: {"Country": r.get("Country")}, filter(check_decline, raw_data)))

        self.sink.write(top_10)
