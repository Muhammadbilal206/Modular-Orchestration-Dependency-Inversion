import plotly.express as px
from typing import List

class ConsoleWriter:
    def write(self, records: List[dict]) -> None:
        for record in records:
            metric = record.get("Metric")
            data = record.get("Data")
            
            print(f"\n--- {metric} ---")
            if not data:
                print("No data available.")
            else:
                for item in data:
                    print(item)
        print("\n----------------------------\n")

class GraphicsChartWriter:
    def write(self, records: List[dict]) -> None:
        for record in records:
            metric = record.get("Metric")
            data = record.get("Data")

            if not data:
                continue

            if metric in ["Top 10 Countries", "Bottom 10 Countries"]:
                fig = px.bar(data, x="GDP", y="Country", orientation='h', title=metric, template="plotly_dark", 
                             color="GDP", color_continuous_scale="Sunsetdark", text_auto=".3s")
                
                fig.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    coloraxis_showscale=False,
                    margin=dict(l=250)
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            elif metric == "Growth Rates":
                data = sorted(data, key=lambda x: x["Growth"], reverse=False)
                
                fig = px.bar(data, x="Growth", y="Country", orientation='h', title=metric, template="plotly_dark", 
                             color="Growth", color_continuous_scale="Tealrose", text_auto=".1f")
                
                chart_height = max(600, len(data) * 25)
                
                fig.update_layout(
                    coloraxis_showscale=False,
                    margin=dict(l=300, r=50, t=50, b=50),
                    height=chart_height
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            elif metric == "Avg GDP Continent":
                fig = px.line(data, x="Year", y="Average_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline")
                fig.update_traces(line=dict(color="#00F0FF", width=4), marker=dict(size=10, color="white"))
                fig.show()

            elif metric == "Global Trend":
                fig = px.line(data, x="Year", y="Total_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline")
                fig.update_traces(line=dict(color="#FF00FF", width=4), marker=dict(size=10, color="white"))
                fig.show()

            elif metric == "Continent Contributions":
                fig = px.pie(data, names="Continent", values="Contribution_Percent", title=metric, 
                             template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05]*len(data))
                fig.show()
