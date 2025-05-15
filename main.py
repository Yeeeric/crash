import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

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

# Setup folium map
m = folium.Map(location=[filtered_df["Latitude"].mean(), filtered_df["Longitude"].mean()], zoom_start=10)

# Add crash points
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=(row["Latitude"], row["Longitude"]),
        radius=4,
        color="red",
        fill=True,
        fill_opacity=0.7,
        popup=f"{row['Crash ID']} ({row['Reporting year']})",
    ).add_to(m)

# Add drawing tool
Draw(export=True).add_to(m)

# Show the map and capture drawn region
st.subheader("Draw a shape on the map to select crashes")
map_data = st_folium(m, width=700, height=500, returned_objects=["last_drawn_feature"])

# Filter to points inside drawn region
def point_in_geojson(point, geojson):
    from shapely.geometry import Point, shape
    return shape(geojson).contains(Point(point[1], point[0]))  # folium = [lat, lon]

if map_data.get("last_drawn_feature"):
    drawn_shape = map_data["last_drawn_feature"]["geometry"]
    selected_df = filtered_df[
        filtered_df.apply(lambda row: point_in_geojson((row["Latitude"], row["Longitude"]), drawn_shape), axis=1)
    ]
    st.success(f"{len(selected_df)} crashes inside selected area")
    st.dataframe(selected_df)
else:
    st.info("Draw a rectangle or shape to filter crashes.")
    st.dataframe(filtered_df)
