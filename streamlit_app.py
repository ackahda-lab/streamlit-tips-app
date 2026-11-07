import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Advertising & Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = Path(__file__).parent / "Advertising_F.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    required = ["TV", "radio", "newspaper", "sales", "City", "latitude", "longitude"]
    missing_columns = [column for column in required if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    return data

st.title("📊 Advertising & Sales Dashboard")
st.write(
    "Explore how TV, radio, and newspaper advertising relate to product sales. "
    "Use the filters and charts to investigate the dataset."
)

try:
    df = load_data()
except FileNotFoundError:
    st.error("The data file Advertising_F.csv was not found. Add it to the same GitHub repository as this app.")
    st.stop()
except Exception as error:
    st.error(f"The dataset could not be loaded: {error}")
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")
cities = sorted(df["City"].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect(
    "Select cities",
    options=cities,
    default=cities
)

filtered_df = df[df["City"].isin(selected_cities)].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters. Choose at least one city.")
    st.stop()

# Key metrics
st.subheader("Overview")
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Records", f"{len(filtered_df):,}")
metric2.metric("Average sales", f"{filtered_df['sales'].mean():.2f}")
metric3.metric("Highest sales", f"{filtered_df['sales'].max():.2f}")
total_ad_spend = (
    filtered_df["TV"].sum()
    + filtered_df["radio"].sum()
    + filtered_df["newspaper"].sum()
)
metric4.metric("Total advertising spend", f"{total_ad_spend:,.1f}")

st.divider()

# Advertising channel comparison
st.subheader("Advertising Spending and Sales")
channel = st.selectbox(
    "Choose an advertising channel",
    ["TV", "radio", "newspaper"]
)
fig_scatter = px.scatter(
    filtered_df,
    x=channel,
    y="sales",
    color="City",
    hover_data=["City"],
    title=f"{channel.title()} Advertising vs. Sales",
    labels={channel: f"{channel.title()} advertising", "sales": "Sales"}
)
fig_scatter.update_layout(legend_title_text="City")
st.plotly_chart(fig_scatter, use_container_width=True)

# Correlation chart
st.subheader("Correlation Between Advertising and Sales")
numeric_columns = ["TV", "radio", "newspaper", "sales"]
correlation = filtered_df[numeric_columns].corr()
fig_corr = px.imshow(
    correlation,
    text_auto=".2f",
    color_continuous_scale="RdBu",
    zmin=-1,
    zmax=1,
    title="Correlation Matrix"
)
st.plotly_chart(fig_corr, use_container_width=True)
st.caption(
    "Correlation ranges from -1 to +1. Values closer to +1 indicate a stronger positive "
    "linear relationship; correlation does not by itself prove causation."
)

# Sales by city
st.subheader("Average Sales by City")
city_sales = (
    filtered_df.groupby("City", as_index=False)["sales"]
    .mean()
    .sort_values("sales", ascending=False)
)
fig_city = px.bar(
    city_sales,
    x="City",
    y="sales",
    color="sales",
    title="Average Sales by City",
    labels={"sales": "Average sales"}
)
st.plotly_chart(fig_city, use_container_width=True)

# Geographic view
st.subheader("City Locations")
city_locations = (
    filtered_df[["City", "latitude", "longitude"]]
    .dropna()
    .drop_duplicates()
    .rename(columns={"latitude": "lat", "longitude": "lon"})
)
if not city_locations.empty:
    st.map(city_locations, latitude="lat", longitude="lon", size=100)
else:
    st.info("No geographic coordinates are available for the selected cities.")

# Data preview and download
st.subheader("Explore the Data")
st.dataframe(filtered_df, use_container_width=True)
csv_download = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered data as CSV",
    data=csv_download,
    file_name="filtered_advertising_data.csv",
    mime="text/csv"
)

with st.expander("Key observations"):
    corr_values = filtered_df[numeric_columns].corr()["sales"].drop("sales").sort_values(ascending=False)
    strongest_channel = corr_values.index[0]
    st.write(
        f"In the currently selected records, **{strongest_channel}** has the strongest "
        f"positive correlation with sales ({corr_values.iloc[0]:.2f})."
    )
    st.write(
        "This is an association in the dataset, not proof that advertising in that channel "
        "causes higher sales."
    )

st.caption("Built with Python, Streamlit, pandas, and Plotly.")
