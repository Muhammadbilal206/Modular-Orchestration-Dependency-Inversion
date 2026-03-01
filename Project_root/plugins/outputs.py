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
                fig = px.bar(data, x="Country", y="GDP", title=metric, template="plotly_dark", 
                             color="GDP", color_continuous_scale="Sunsetdark", text_auto=".3s")
                
                fig.update_layout(
                    xaxis={'categoryorder':'total descending'},
                    xaxis_tickangle=-45,
                    coloraxis_showscale=False,
                    margin=dict(b=120)
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            elif metric == "Growth Rates":
                data = sorted(data, key=lambda x: x["Growth"], reverse=True)
                
                fig = px.bar(data, x="Country", y="Growth", title=metric, template="plotly_dark", 
                             color="Growth", color_continuous_scale="Tealrose", text_auto=".1f")
                
                fig.update_layout(
                    xaxis_tickangle=-45,
                    coloraxis_showscale=False,
                    margin=dict(b=150, t=50, l=50, r=50),
                    uniformtext_minsize=9, 
                    uniformtext_mode='hide'
                )
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            elif metric == "Avg GDP Continent":
                fig = px.line(data, x="Year", y="Average_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline")
                fig.update_traces(line=dict(color="#00F0FF", width=4), marker=dict(size=10, color="white"))
                fig.update_layout(margin=dict(b=50))
                fig.show()

            elif metric == "Global Trend":
                fig = px.line(data, x="Year", y="Total_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline")
                fig.update_traces(line=dict(color="#FF00FF", width=4), marker=dict(size=10, color="white"))
                fig.update_layout(margin=dict(b=50))
                fig.show()

            elif metric == "Continent Contributions":
                fig = px.pie(data, names="Continent", values="Contribution_Percent", title=metric, 
                             template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05]*len(data))
                fig.show()
