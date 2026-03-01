import plotly.express as px
import plotly.graph_objects as go
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
        # Dictionary to globally apply bold formatting and clearer names to all axes
        bold_labels = {
            "Country": "<b>Country</b>",
            "GDP": "<b>GDP (US$)</b>",
            "Growth": "<b>Growth Rate (%)</b>",
            "Year": "<b>Year</b>",
            "Average_GDP": "<b>Average GDP (US$)</b>",
            "Total_GDP": "<b>Total Global GDP (US$)</b>",
            "Continent": "<b>Continent</b>"
        }

        for record in records:
            metric = record.get("Metric")
            data = record.get("Data")

            if not data:
                continue

            # 1 & 2. Top 10 and Bottom 10 Countries
            if metric in ["Top 10 Countries", "Bottom 10 Countries"]:
                fig = px.bar(data, x="GDP", y="Country", orientation='h', title=metric, template="plotly_dark", 
                             color="GDP", color_continuous_scale="Sunsetdark", text_auto=".3s",
                             labels=bold_labels)
                
                fig.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    margin=dict(l=250, r=100)
                )
                fig.update_xaxes(title_font=dict(size=18, color="white"))
                fig.update_yaxes(title_font=dict(size=18, color="white"))
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            # 3. Growth Rates
            elif metric == "Growth Rates":
                data = sorted(data, key=lambda x: x["Growth"], reverse=False)
                
                fig = px.bar(data, x="Growth", y="Country", orientation='h', title=metric, template="plotly_dark", 
                             color="Growth", color_continuous_scale="Tealrose", text_auto=".1f",
                             labels=bold_labels)
                
                chart_height = max(600, len(data) * 25)
                
                fig.update_layout(
                    margin=dict(l=300, r=100, t=50, b=50),
                    height=chart_height
                )
                fig.update_xaxes(title_font=dict(size=18, color="white"))
                fig.update_yaxes(title_font=dict(size=18, color="white"))
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            # 4. Average GDP by Continent
            elif metric == "Avg GDP Continent":
                fig = px.line(data, x="Year", y="Average_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline", labels=bold_labels)
                fig.update_traces(line=dict(color="#00F0FF", width=4), marker=dict(size=10, color="white"))
                fig.update_xaxes(title_font=dict(size=18, color="white"))
                fig.update_yaxes(title_font=dict(size=18, color="white"))
                fig.show()

            # 5. Global Trend
            elif metric == "Global Trend":
                fig = px.line(data, x="Year", y="Total_GDP", title=metric, template="plotly_dark", 
                              markers=True, line_shape="spline", labels=bold_labels)
                fig.update_traces(line=dict(color="#FF00FF", width=4), marker=dict(size=10, color="white"))
                fig.update_xaxes(title_font=dict(size=18, color="white"))
                fig.update_yaxes(title_font=dict(size=18, color="white"))
                fig.show()

            # 6. Fastest Growing Continent
            elif metric == "Fastest Growing Continent":
                # Ensure data is in a list format for Plotly
                if isinstance(data, dict):
                    data = [data]
                fig = px.bar(data, x="Continent", y="Growth", title=metric, template="plotly_dark", 
                             color="Growth", color_continuous_scale="Tealrose", text_auto=".2f",
                             labels=bold_labels)
                fig.update_xaxes(title_font=dict(size=18, color="white"))
                fig.update_yaxes(title_font=dict(size=18, color="white"))
                fig.update_traces(textposition='outside', cliponaxis=False)
                fig.show()

            # 7. Declining Countries
            elif metric == "Declining Countries":
                countries = [item["Country"] for item in data]
                fig = go.Figure(data=[go.Table(
                    header=dict(values=[f"<b>{metric}</b>"], 
                                fill_color='#2a2a2a', 
                                align='center', 
                                font=dict(color='white', size=16)),
                    cells=dict(values=[countries], 
                               fill_color='#111111', 
                               align='center', 
                               font=dict(color='white', size=14))
                )])
                fig.update_layout(title=metric, template="plotly_dark", margin=dict(t=50, b=50))
                fig.show()

            # 8. Continent Contributions
            elif metric == "Continent Contributions":
                fig = px.pie(data, names="Continent", values="Contribution_Percent", title=metric, 
                             template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05]*len(data))
                fig.show()
