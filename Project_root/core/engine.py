from typing import List, Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__(self, sink: DataSink, params: dict):
        self.sink = sink
        self.params = params

    def execute(self, raw_data: List[Any]) -> None:
        if not raw_data:
            return

        try:
            target_continent = str(self.params["target_continent"]).strip()
            target_year = str(self.params["target_year"]).strip()
            start_year = int(self.params["start_year"])
            end_year = int(self.params["end_year"])
            decline_years = int(self.params["decline_years"])
        except KeyError as e:
            raise ValueError(f"Configuration Error: Missing required parameter {e} in config.json")

        if start_year > end_year:
            raise ValueError(f"Data Error: start_year ({start_year}) cannot be greater than end_year ({end_year}).")

        available_columns = [str(k).strip() for k in raw_data[0].keys()]
        for year in [target_year, str(start_year), str(end_year)]:
            if year not in available_columns:
                year_cols = [int(y) for y in available_columns if y.isdigit()]
                min_y, max_y = (min(year_cols), max(year_cols)) if year_cols else ("Unknown", "Unknown")
                raise ValueError(f"Data Error: The year '{year}' does not exist in the dataset. Available years are {min_y} to {max_y}.")

        available_continents = set(str(r.get('Continent', '')).strip() for r in raw_data if r.get('Continent'))
        valid_continents = [c for c in available_continents if c and c.lower() != "nan"]
        
        valid_continents_lower = [c.lower() for c in valid_continents]
        if target_continent.lower() not in valid_continents_lower:
            raise ValueError(f"Data Error: The continent '{target_continent}' does not exist in the dataset. Available options are: {', '.join(sorted(valid_continents))}.")
        
        for c in valid_continents:
            if c.lower() == target_continent.lower():
                target_continent = c
                break

        def get_gdp(row, year):
            val = row.get(str(year))
            if val is None or str(val).strip() == "" or str(val).lower() == "nan":
                return 0.0
            try:
                return float(str(val).replace(',', '').replace('"', '').strip())
            except (ValueError, TypeError):
                return 0.0

        def get_name(row):
            name = row.get("Country Name")
            if name is None or str(name).strip() == "":
                return "Unknown"
            
            name_str = str(name).strip()
            invalid_terms = ["income", "IBRD", "IDA", "World", "Total", "Asia &", "Europe &", "Africa ", "Sub-Saharan", "OECD", "Euro area"]
            for term in invalid_terms:
                if term.lower() in name_str.lower():
                    return "Unknown"
            return name_str

        continent_data = list(filter(lambda r: str(r.get('Continent', '')).strip() == target_continent, raw_data))
        
        mapped_gdp = list(map(lambda r: {"Country": get_name(r), "GDP": get_gdp(r, target_year)}, continent_data))
        valid_gdp = list(filter(lambda x: x["GDP"] > 0 and x["Country"] != "Unknown", mapped_gdp))
        top_10 = sorted(valid_gdp, key=lambda x: x["GDP"], reverse=True)[:10]
        bottom_10 = sorted(valid_gdp, key=lambda x: x["GDP"])[:10]

        def calc_growth(row):
            start = get_gdp(row, start_year)
            end = get_gdp(row, end_year)
            if start <= 0: return {"Country": get_name(row), "Growth": 0.0}
            return {"Country": get_name(row), "Growth": ((end - start) / start) * 100}
        
        growth_rates = list(filter(lambda x: x["Growth"] != 0 and x["Country"] != "Unknown", map(calc_growth, continent_data)))

        years_range = list(range(start_year, end_year + 1))
        avg_gdp_continent = [{"Year": y, "Average_GDP": sum(gdps)/len(gdps) if (gdps := [get_gdp(r, y) for r in continent_data if get_gdp(r, y) > 0]) else 0} for y in years_range]
        global_trend = [{"Year": y, "Total_GDP": sum(get_gdp(r, y) for r in raw_data)} for y in years_range]

        continents = list(set(str(r.get('Continent', '')).strip() for r in raw_data if r.get('Continent')))
        valid_continents_growth = [c for c in continents if c and c.lower() != "nan"]
        
        def continent_growth(cont):
            cont_rows = [r for r in raw_data if str(r.get('Continent', '')).strip() == cont]
            start_total = sum(get_gdp(r, start_year) for r in cont_rows)
            end_total = sum(get_gdp(r, end_year) for r in cont_rows)
            if start_total <= 0: return {"Continent": cont, "Growth": 0.0}
            return {"Continent": cont, "Growth": ((end_total - start_total) / start_total) * 100}
            
        continent_growths = list(map(continent_growth, valid_continents_growth))
        fastest_continent = sorted(continent_growths, key=lambda x: x["Growth"], reverse=True)[0] if continent_growths else {}

        def check_decline(row):
            years = [end_year - i for i in range(decline_years + 1)]
            gdps = [get_gdp(row, y) for y in years]
            if 0.0 in gdps:
                return False
            declines = [gdps[i] < gdps[i+1] for i in range(len(gdps)-1)]
            return all(declines) and len(declines) > 0

        declining_countries = [{"Country": get_name(r)} for r in raw_data if check_decline(r) and get_name(r) != "Unknown"]

        global_total = sum(get_gdp(r, target_year) for r in raw_data)
        contributions = [{"Continent": c, "Contribution_Percent": (sum(get_gdp(r, target_year) for r in raw_data if str(r.get('Continent')).strip() == c) / global_total * 100)} for c in valid_continents_growth if global_total > 0]

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
