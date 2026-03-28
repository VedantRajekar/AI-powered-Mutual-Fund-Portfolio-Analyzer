import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def format_inr(value: float) -> str:
    if value >= 1e7:
        return f"₹{value/1e7:.2f} Cr"
    elif value >= 1e5:
        return f"₹{value/1e5:.2f} L"
    return f"₹{value:,.2f}"

def plot_allocation_pie(df: pd.DataFrame) -> go.Figure:
    fig = px.pie(
        df,
        values="current_value",
        names="fund_name",
        title="Portfolio Allocation",
        hole=0.4
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(showlegend=False, height=450)
    return fig

def plot_amc_bar(df: pd.DataFrame) -> go.Figure:
    amc_df = df.groupby("amc")["current_value"].sum().reset_index()
    amc_df = amc_df.sort_values("current_value", ascending=True)

    fig = px.bar(
        amc_df,
        x="current_value",
        y="amc",
        orientation="h",
        title="Exposure by AMC",
        labels={"current_value": "Value (Rs.)", "amc": "AMC"}
    )
    fig.update_layout(height=400)
    return fig