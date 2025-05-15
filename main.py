import streamlit as st
import pandas as pd
import pydeck as pdk

# Load the crash data
@st.cache_data
def load_data():
    df = pd.read_csv("data/2019_2023_crash_simple.csv")
    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

df = load_data()

st.title("Crash Data Map (2019–2023)")

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df["Reporting year"].dropna().unique())
degrees = sorted(df["Degree of crash - detailed"].dropna().unique())

selected_years = st.sidebar.multiselect("Reporting Year", years, default=years)
selected_degrees = st.sidebar.multiselect("Degree of Crash", degrees, default=degrees)

# Filter the DataFrame
filtered_df = df[
    (df["Reporting year"].isin(selected_years)) &
    (df["Degree of crash - detailed"].isin(selected_degrees))
]

st.subheader(f"Total crashes: {len(filtered_df)}")

# Map visualization
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=filtered_df["Latitude"].mean(),
        longitude=filtered_df["Longitude"].mean(),
        zoom=10,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[Longitude, Latitude]",
            get_color="[200, 30, 0, 160]",
            get_radius=40,
            pickable=True
        ),
    ],
    tooltip={"text": "Crash ID: {Crash ID}\nYear: {Reporting year}\nSeverity: {Degree of crash - detailed}"}
))

# Use Streamlit's built-in map selection tool
st.subheader("Click-and-drag to select points (below)")

map_df = filtered_df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
st.map(data=map_df[["latitude", "longitude"]], use_container_width=True)

# Display table with filtered data
st.subheader("Filtered Crash Data")
st.dataframe(filtered_df)
