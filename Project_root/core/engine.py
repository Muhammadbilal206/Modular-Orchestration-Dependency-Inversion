from typing import List, Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__(self, sink: DataSink, params: dict):
        self.sink = sink
        self.params = params

    def execute(self, raw_data: List[Any]) -> None:
        target_continent = self.params.get("target_continent")
        target_year = str(self.params.get("target_year"))
        start_year = int(self.params.get("start_year"))
        end_year = int(self.params.get("end_year"))
        decline_years = int(self.params.get("decline_years"))

        def get_gdp(row, year):
            try:
                return float(row.get(str(year), 0))
            except (ValueError, TypeError):
                return 0.0

        continent_data = list(filter(lambda r: r.get('Continent') == target_continent, raw_data))
        
        mapped_gdp = list(map(lambda r: {"Country": r.get("Country", ""), "GDP": get_gdp(r, target_year)}, continent_data))
        valid_gdp = list(filter(lambda x: x["GDP"] > 0, mapped_gdp))
        
        top_10 = sorted(valid_gdp, key=lambda x: x["GDP"], reverse=True)[:10]
        bottom_10 = sorted(valid_gdp, key=lambda x: x["GDP"])[:10]

        def calc_growth(row):
            start = get_gdp(row, start_year)
            end = get_gdp(row, end_year)
            if start == 0:
                return {"Country": row.get("Country"), "Growth": 0.0}
            return {"Country": row.get("Country"), "Growth": ((end - start) / start) * 100}

        growth_rates = list(map(calc_growth, continent_data))

        years_range = list(range(start_year, end_year + 1))
        
        def avg_for_year(year):
            gdps = list(filter(lambda x: x > 0, map(lambda r: get_gdp(r, year), continent_data)))
            return sum(gdps) / len(gdps) if gdps else 0.0
            
        avg_gdp_continent = list(map(lambda y: {"Year": y, "Average_GDP": avg_for_year(y)}, years_range))

        def global_total_for_year(year):
            return sum(map(lambda r: get_gdp(r, year), raw_data))

        global_trend = list(map(lambda y: {"Year": y, "Total_GDP": global_total_for_year(y)}, years_range))

        continents = list(set(map(lambda r: r.get('Continent'), raw_data)))
        valid_continents = list(filter(None, continents))

        def continent_growth(cont):
            cont_rows = list(filter(lambda r: r.get('Continent') == cont, raw_data))
            start_total = sum(map(lambda r: get_gdp(r, start_year), cont_rows))
            end_total = sum(map(lambda r: get_gdp(r, end_year), cont_rows))
            if start_total == 0:
                return {"Continent": cont, "Growth": 0.0}
            return {"Continent": cont, "Growth": ((end_total - start_total) / start_total) * 100}

        continent_growths = list(map(continent_growth, valid_continents))
        fastest_continent = sorted(continent_growths, key=lambda x: x["Growth"], reverse=True)[0] if continent_growths else {}

        def check_decline(row):
            years = [end_year - i for i in range(decline_years + 1)]
            gdps = [get_gdp(row, y) for y in years]
            if 0.0 in gdps:
                return False
            declines = list(map(lambda i: gdps[i] < gdps[i+1], range(len(gdps)-1)))
            return all(declines) and len(declines) > 0

        declining_countries = list(map(lambda r: {"Country": r.get("Country")}, filter(check_decline, raw_data)))

        global_total_target = global_total_for_year(target_year)
        
        def cont_contribution(cont):
            cont_rows = list(filter(lambda r: r.get('Continent') == cont, raw_data))
            cont_total = sum(map(lambda r: get_gdp(r, target_year), cont_rows))
            contrib = (cont_total / global_total_target * 100) if global_total_target > 0 else 0.0
            return {"Continent": cont, "Contribution_Percent": contrib}

        contributions = list(map(cont_contribution, valid_continents))

        final_output = [
            {"Metric": "Top 10 Countries", "Data": top_10},
            {"Metric": "Bottom 10 Countries", "Data": bottom_10},
            {"Metric": "Growth Rates", "Data": growth_rates},
            {"Metric": "Avg GDP Continent", "Data": avg_gdp_continent},
            {"Metric": "Global Trend", "Data": global_trend},
            {"Metric": "Fastest Growing Continent", "Data": [fastest_continent]},
            {"Metric": "Declining Countries", "Data": declining_countries},
            {"Metric": "Continent Contributions", "Data": contributions}
        ]

        self.sink.write(final_output)
