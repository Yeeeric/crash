import streamlit as st
import pandas as pd
import folium
from folium.plugins import Draw, MarkerCluster
from streamlit_folium import st_folium
from shapely.geometry import Point, shape

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Crash Map Viewer", layout="wide")

# Load crash data
@st.cache_data
def load_data():
    df = pd.read_csv("data/2019_2023_crash_simple.csv")
    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

df = load_data()

st.title("Crash Map Viewer (2019–2023)")

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df["Reporting year"].dropna().unique())
degrees = sorted(df["Degree of crash - detailed"].dropna().unique())

selected_years = st.sidebar.multiselect("Reporting Year", years, default=years)
selected_degrees = st.sidebar.multiselect("Degree of Crash", degrees, default=degrees)

# Filter data
filtered_df = df[
    (df["Reporting year"].isin(selected_years)) &
    (df["Degree of crash - detailed"].isin(selected_degrees))
]

st.write(f"Showing {len(filtered_df):,} crashes on the map")

# Create map centered on mean crash location
m = folium.Map(
    location=[filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()],
    zoom_start=10
)

# Add clustered crash markers
marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    folium.Marker(
        location=(row["Latitude"], row["Longitude"]),
        popup=f"""
            <b>Crash ID:</b> {row['Crash ID']}<br>
            <b>Year:</b> {row['Reporting year']}<br>
            <b>Severity:</b> {row['Degree of crash - detailed']}<br>
            <b>Description:</b> {row['RUM - description']}
        """,
    ).add_to(marker_cluster)

# Add drawing tool for region selection
Draw(export=True).add_to(m)

# Render map in Streamlit and capture drawn shape
st.subheader("Draw a shape to select crashes")
map_data = st_folium(m, width=900, height=600, returned_objects=["last_drawn_feature"])

# Helper: Check if a point is in the drawn shape
def point_in_geojson(point, geojson):
    return shape(geojson).contains(Point(point[1], point[0]))  # folium = [lat, lon]

# If shape is drawn, filter data
if map_data.get("last_drawn_feature"):
    drawn_shape = map_data["last_drawn_feature"]["geometry"]
    with st.spinner("Filtering crashes inside selected area..."):
        selected_df = filtered_df[
            filtered_df.apply(lambda row: point_in_geojson((row["Latitude"], row["Longitude"]), drawn_shape), axis=1)
        ]
    st.success(f"{len(selected_df)} crashes inside selected region.")
    st.dataframe(selected_df)
else:
    st.info("Draw a rectangle or shape to filter crashes.")
    st.dataframe(filtered_df.head(1000), use_container_width=True)
