from typing import List, Any
from core.contracts import DataSink

class TransformationEngine:
    def __init__(self, sink: DataSink, params: dict):
        self.sink = sink
        self.params = params

    def execute(self, raw_data: List[Any]) -> None:
        if not raw_data:
            return

        target_continent = str(self.params.get("target_continent", "Asia"))
        target_year = str(self.params.get("target_year", "2023"))
        start_year = int(self.params.get("start_year", 2010))
        end_year = int(self.params.get("end_year", 2023))
        decline_years = int(self.params.get("decline_years", 5))

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

        # Filter for Target Continent
        continent_data = list(filter(lambda r: str(r.get('Continent', '')).strip() == target_continent, raw_data))
        
        # 1 & 2. Top 10 and Bottom 10
        mapped_gdp = list(map(lambda r: {"Country": get_name(r), "GDP": get_gdp(r, target_year)}, continent_data))
        valid_gdp = list(filter(lambda x: x["GDP"] > 0 and x["Country"] != "Unknown", mapped_gdp))
        top_10 = sorted(valid_gdp, key=lambda x: x["GDP"], reverse=True)[:10]
        bottom_10 = sorted(valid_gdp, key=lambda x: x["GDP"])[:10]

        # 3. Growth Rates
        def calc_growth(row):
            start = get_gdp(row, start_year)
            end = get_gdp(row, end_year)
            if start <= 0: return {"Country": get_name(row), "Growth": 0.0}
            return {"Country": get_name(row), "Growth": ((end - start) / start) * 100}
        growth_rates = list(filter(lambda x: x["Growth"] != 0 and x["Country"] != "Unknown", map(calc_growth, continent_data)))

        # 4 & 5. Average Continent Trend and Global Trend
        years_range = list(range(start_year, end_year + 1))
        avg_gdp_continent = [{"Year": y, "Average_GDP": sum(gdps)/len(gdps) if (gdps := [get_gdp(r, y) for r in continent_data if get_gdp(r, y) > 0]) else 0} for y in years_range]
        global_trend = [{"Year": y, "Total_GDP": sum(get_gdp(r, y) for r in raw_data)} for y in years_range]

        # 6. Fastest Growing Continent (Restored)
        continents = list(set(str(r.get('Continent', '')).strip() for r in raw_data if r.get('Continent')))
        valid_continents = [c for c in continents if c and c.lower() != "nan"]
        
        def continent_growth(cont):
            cont_rows = [r for r in raw_data if str(r.get('Continent', '')).strip() == cont]
            start_total = sum(get_gdp(r, start_year) for r in cont_rows)
            end_total = sum(get_gdp(r, end_year) for r in cont_rows)
            if start_total <= 0: return {"Continent": cont, "Growth": 0.0}
            return {"Continent": cont, "Growth": ((end_total - start_total) / start_total) * 100}
            
        continent_growths = list(map(continent_growth, valid_continents))
        fastest_continent = sorted(continent_growths, key=lambda x: x["Growth"], reverse=True)[0] if continent_growths else {}

        # 7. Declining Countries (Restored)
        def check_decline(row):
            years = [end_year - i for i in range(decline_years + 1)]
            gdps = [get_gdp(row, y) for y in years]
            if 0.0 in gdps:
                return False
            declines = [gdps[i] < gdps[i+1] for i in range(len(gdps)-1)] # Checks if recent year is less than previous year
            return all(declines) and len(declines) > 0

        declining_countries = [{"Country": get_name(r)} for r in raw_data if check_decline(r) and get_name(r) != "Unknown"]

        # 8. Continent Contributions
        global_total = sum(get_gdp(r, target_year) for r in raw_data)
        contributions = [{"Continent": c, "Contribution_Percent": (sum(get_gdp(r, target_year) for r in raw_data if str(r.get('Continent')).strip() == c) / global_total * 100)} for c in valid_continents if global_total > 0]

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
