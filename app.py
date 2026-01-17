import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Nexus Tech Sales Dashboard",
    layout="wide"
)

# Data loading
@st.cache_data
def load_data():
    df = pd.read_csv("Nexus_Tech_dataset.csv") 
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# SIDEBAR FILTERS
st.sidebar.title("🔍 Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min(), df["Date"].max()]
)

categories = st.sidebar.multiselect(
    "Product Category",
    df["Product_Category"].unique(),
    default=df["Product_Category"].unique()
)

regions = st.sidebar.multiselect(
    "Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

channels = st.sidebar.multiselect(
    "Sales Channel",
    df["Sales_Channel"].unique(),
    default=df["Sales_Channel"].unique()
)

# SCENARIO SIMULATOR SIDEBAR

st.sidebar.divider()
st.sidebar.title("🚀 Scenario Simulator")
st.sidebar.write("Adjust variables to see projected profit impact.")

marketing_boost = st.sidebar.slider("Marketing Spend Increase (%)", 0, 100, 0)
efficiency_gain = st.sidebar.slider("Operational Efficiency Gain (%)", 0, 50, 0)

# FILTER LOGIC
filtered_df = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1])) &
    (df["Product_Category"].isin(categories)) &
    (df["Region"].isin(regions)) &
    (df["Sales_Channel"].isin(channels))
].copy()

# SIMULATION LOGIC
sim_rev_mult = 1 + (marketing_boost / 100) * 0.2 
sim_margin_bonus = (efficiency_gain / 100)

filtered_df["Sim_Revenue"] = filtered_df["Total_Revenue"] * sim_rev_mult
filtered_df["Sim_Profit"] = filtered_df["Sim_Revenue"] * (filtered_df["Profit_Margin"] + sim_margin_bonus)

# MAIN UI
st.title("📊 Nexus Tech Sales Analytics Dashboard")
st.info("💡 Use the sidebar filters to drill down or use the **Scenario Simulator** to forecast growth.")

# KPI Metrics
total_rev = filtered_df["Total_Revenue"].sum()
sim_rev = filtered_df["Sim_Revenue"].sum()
total_prof = filtered_df["Net_Profit"].sum()
sim_prof = filtered_df["Sim_Profit"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${total_rev:,.2f}", f"${sim_rev - total_rev:,.2f} Sim")
col2.metric("📈 Net Profit", f"${total_prof:,.2f}", f"${sim_prof - total_prof:,.2f} Sim")
col3.metric("📊 Avg Margin", f"{filtered_df['Profit_Margin'].mean():.2%}", f"{sim_margin_bonus:.2%}")
col4.metric("🧾 Total Orders", filtered_df["Order_ID"].nunique())

st.divider()

# VISUALIZATIONS

# ROW 1: Donut and Line Chart
left_top, right_top = st.columns(2)

with left_top:
    channel_data = filtered_df.groupby("Sales_Channel")["Total_Revenue"].sum().reset_index()
    fig_donut = px.pie(channel_data, names="Sales_Channel", values="Total_Revenue", 
                       hole=0.6, title="Revenue Split by Sales Channel")
    st.plotly_chart(fig_donut, use_container_width=True)

with right_top:
    monthly_df = filtered_df.set_index("Date").resample("M")[["Total_Revenue", "Sim_Revenue"]].sum().reset_index()
    fig_line = px.line(monthly_df, x="Date", y=["Total_Revenue", "Sim_Revenue"], 
                       markers=True, title="Actual vs. Simulated Revenue Trend")
    st.plotly_chart(fig_line, use_container_width=True)

# ROW 2: Map and Bar Chart
left_bot, right_bot = st.columns(2)

with left_bot:
    region_data = filtered_df.groupby("Region")["Total_Revenue"].sum().reset_index()
    region_map = {"North America": "USA", "Europe": "FRA", "Asia": "CHN", "South America": "BRA", "Africa": "NGA"}
    region_data["Country"] = region_data["Region"].map(region_map)

    fig_map = px.choropleth(
        region_data,
        locations="Country",
        color="Total_Revenue",
        hover_name="Region",
        color_continuous_scale="Blues",
        title="Revenue by Region"
    )

    fig_map.add_scattergeo(
        locations=region_data["Country"],
        text=region_data["Region"],
        mode="text",
        textfont=dict(
            color="black",
            size=14
        )
    )


    st.plotly_chart(fig_map, use_container_width=True)

with right_bot:
    cat_data = filtered_df.groupby("Product_Category")["Total_Revenue"].sum().reset_index()
    fig_bar = px.bar(cat_data, x="Total_Revenue", y="Product_Category", 
                     orientation='h', title="Revenue by Product Category")
    st.plotly_chart(fig_bar, use_container_width=True)

# Data Preview
st.divider()
st.subheader("📄 Filtered & Simulated Data Preview")
st.dataframe(filtered_df.head(10), use_container_width=True)