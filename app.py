import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from typing import List
import os

# Page configuration
st.set_page_config(
    page_title="DOOH Screens Dashboard",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #2B0030; /* MiQ Midnight Blue */
        padding-bottom: 10px;
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }

    /* Sidebar selected tags (multiselect chips) */
    .stSidebar [data-baseweb="tag"] {
        background-color: #2B0030 !important;
        color: #ffffff !important;
        border-color: #2B0030 !important;
    }
    .stSidebar [data-baseweb="tag"] svg path {
        fill: #ffffff !important; /* close icon */
    }

    /* Sidebar dropdown selected option highlight */
    .stSidebar [data-baseweb="select"] [aria-selected="true"] {
        background-color: rgba(43, 0, 48, 0.12) !important;
        color: #2B0030 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data(cntry: str) -> pd.DataFrame:
    """Load and preprocess the DOOH screens data"""
    if cntry == 'SG':
        df = pd.read_csv('DOOH_Screens_data_SG.csv', encoding='cp1252')
    elif cntry == 'HK':
        df = pd.read_csv('DOOH_Screens_data_HK.csv', encoding='utf-8')
    
    # Clean column names (remove trailing spaces)
    df.columns = df.columns.str.strip()
    
    # Convert Allow Image and Allow Video to readable format (robust to strings/ints)
    if 'Allow Image' in df.columns:
        df['Allow Image'] = (
            df['Allow Image']
            .astype(str)
            .str.strip()
            .map({'1': 'Yes', '0': 'No', 'Yes': 'Yes', 'No': 'No'})
            .fillna('Unknown')
        )
    if 'Allow Video' in df.columns:
        df['Allow Video'] = (
            df['Allow Video']
            .astype(str)
            .str.strip()
            .map({'1': 'Yes', '0': 'No', 'Yes': 'Yes', 'No': 'No'})
            .fillna('Unknown')
        )
    # Ensure numeric spot length
    if 'Spot length' in df.columns:
        df['Spot length'] = pd.to_numeric(df['Spot length'], errors='coerce')
    
    # Ensure numeric types
    df['Screen latitude'] = pd.to_numeric(df['Screen latitude'], errors='coerce')
    df['Screen longitude'] = pd.to_numeric(df['Screen longitude'], errors='coerce')
    
    # Remove rows with missing coordinates
    df = df.dropna(subset=['Screen latitude', 'Screen longitude'])
    
    return df

# Helper: multiselect with an 'All' option (sidebar), without mutating widget state
def multiselect_with_all(label: str, options: list, key: str, *, in_sidebar: bool = True):
    all_token = 'All'
    options_with_all = [all_token] + options
    container = st.sidebar if in_sidebar else st
    # Use a separate internal key so we never write to the widget's state
    raw_key = f"{key}__raw"
    selection = container.multiselect(label, options_with_all, default=[all_token], key=raw_key)
    # Compute effective selection for filtering
    if (all_token in selection) or (len(selection) == 0):
        # Treat as selecting all specific options
        return options, True
    else:
        return selection, False

def load_country_data(country: str) -> pd.DataFrame:
    # Load the data
    try:
        df = load_data(country)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()



st.markdown(
    """
    <div style="text-align: right;">
        <img src="https://www.wearemiq.com/_nuxt/logo.B0baRclm.png" width="70">
    </div>
    """,
    unsafe_allow_html=True,
)

# Header    
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 0.5rem; padding-left: 0px;">
        <h1 style="margin: 0;">📍 DOOH Screens Dashboard</h1>
        <h3 style="margin: 0; padding-left: 70px; font-weight: 500; color: #2B0030;">Explore Digital Out-of-Home Screen Locations</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Country filter (single select; no 'All')
country_options = ['Singapore', 'Hong Kong']
selected_country = st.sidebar.selectbox("Country", country_options, index=0)

# Get the country data
if selected_country == 'Singapore':
    df = load_country_data('SG')
elif selected_country == 'Hong Kong':
    df = load_country_data('HK')

# Region filter (multi-select with All, depends on selected country)
region_base = df[df['Country'] == selected_country]
region_options = sorted(region_base['Site region (state)'].dropna().unique().tolist())
selected_regions, regions_all = multiselect_with_all("Region", region_options, key="filter_region")

# Dimensions filter (multi-select with All)
dimension_options = sorted(df['Dimensions (W x H)'].dropna().unique().tolist())
selected_dimensions, dims_all = multiselect_with_all("Dimensions (W x H)", dimension_options, key="filter_dimensions")

# Allow Video filter (multi-select with All)
allow_video_options = ["Yes", "No"]
selected_allow_video, allow_video_all = multiselect_with_all(
    "Allow Video", allow_video_options, key="filter_allow_video"
)

# Spot Length filter (multi-select with All)
spot_lengths_all = sorted([int(x) for x in df['Spot length'].dropna().unique().tolist()])
selected_spot_lengths, spots_all = multiselect_with_all("Spot Length (s)", spot_lengths_all, key="filter_spot_length")

# Venue Type filter (multi-select with All)
venue_type_options = sorted(df['Venue type'].dropna().unique().tolist())
selected_venue_types, vt_all = multiselect_with_all("Venue Type", venue_type_options, key="filter_venue_type")

# Apply filters
filtered_df = df.copy()

filtered_df = filtered_df[filtered_df['Country'] == selected_country]

if selected_regions and not regions_all:
    filtered_df = filtered_df[filtered_df['Site region (state)'].isin(selected_regions)]

if selected_dimensions and not dims_all:
    filtered_df = filtered_df[filtered_df['Dimensions (W x H)'].isin(selected_dimensions)]

if selected_allow_video and not allow_video_all:
    filtered_df = filtered_df[filtered_df['Allow Video'].isin(selected_allow_video)]

if selected_spot_lengths and not spots_all:
    filtered_df = filtered_df[filtered_df['Spot length'].isin(selected_spot_lengths)]

if selected_venue_types and not vt_all:
    filtered_df = filtered_df[filtered_df['Venue type'].isin(selected_venue_types)]

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Screens", len(filtered_df))

# with col2:
#     st.metric("Countries", filtered_df['Country'].nunique())

with col2:
    st.metric("Media Owners", filtered_df['Media owner'].nunique())

with col3:
    image_allowed = len(filtered_df[filtered_df['Allow Image'] == 'Yes'])
    st.metric("Image Enabled", image_allowed)

with col4:
    video_allowed = len(filtered_df[filtered_df['Allow Video'] == 'Yes'])
    st.metric("Video Enabled", video_allowed)

st.markdown("---")

st.subheader("🗺️ Screens Location")

if len(filtered_df) > 0:
    # Prepare data for map with tooltip information
    map_data = filtered_df[['Screen latitude', 'Screen longitude', 'Screen name', 
                             'Venue type', 'Media owner', 'Site location (city)', 
                             'Dimensions (W x H)', 'Allow Image', 'Allow Video', 
                             'Spot length']].copy()
    
    map_data.columns = ['lat', 'lon', 'Screen Name', 'Venue Type', 'Media Owner', 
                       'City', 'Dimensions', 'Allow Image', 'Allow Video', 'Spot Length']
    
    # Calculate center point
    center_lat = map_data['lat'].mean()
    center_lon = map_data['lon'].mean()
    
    # Determine zoom level based on data spread
    lat_range = map_data['lat'].max() - map_data['lat'].min()
    lon_range = map_data['lon'].max() - map_data['lon'].min()
    
    if lat_range < 0.1 and lon_range < 0.1:
        zoom_level = 12
    elif lat_range < 0.5 and lon_range < 0.5:
        zoom_level = 10
    else:
        zoom_level = 8
    
    # Brand color for pins: MiQ Orange with alpha
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_data,
        get_position=['lon', 'lat'],
        get_color='[255, 101, 0, 180]',
        get_radius=100,
        pickable=True,
        auto_highlight=True,
    )
    
    # Set the viewport location
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=zoom_level,
        pitch=0,
    )
    
    # Create tooltip
    tooltip = {
        "html": """
        <div style=\"background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);\">\n            <b style=\"color: #2B0030; font-size: 14px;\">{Screen Name}</b><br/>\n            <hr style=\"margin: 5px 0; border: none; border-top: 1px solid #ddd;\">\n            <b>Venue Type:</b> {Venue Type}<br/>\n            <b>Media Owner:</b> {Media Owner}<br/>\n            <b>City:</b> {City}<br/>\n            <b>Dimensions:</b> {Dimensions}<br/>\n            <b>Allow Image:</b> {Allow Image}<br/>\n            <b>Allow Video:</b> {Allow Video}<br/>\n            <b>Spot Length:</b> {Spot Length}s\n        </div>\n        """,
        "style": {
            "backgroundColor": "white",
            "color": "black"
        }
    }
    
    # Render the map, using Mapbox style if token available; else default
    deck_kwargs = {
        "layers": [layer],
        "initial_view_state": view_state,
        "tooltip": tooltip,
    }
    if os.getenv("MAPBOX_API_KEY"):
        deck_kwargs["map_style"] = 'mapbox://styles/mapbox/light-v10'
    st.pydeck_chart(pdk.Deck(**deck_kwargs), use_container_width=True)
else:
    st.warning("No screens match the selected filters.")

# Tabs for analytics and details below the map
tabs = st.tabs(["📊 Analytics", "📋 Detailed Screen Information"])

with tabs[0]:
    if len(filtered_df) > 0:
        brand_seq = ["#FF6500", "#FFCA01", "#FF2000", "#EA00AD", "#2B0030"]
        # Venue Type Distribution
        venue_counts = filtered_df['Venue type'].value_counts().head(10)
        fig1 = px.bar(
            x=venue_counts.values,
            y=venue_counts.index,
            orientation='h',
            title='Top 10 Venue Types',
            labels={'x': 'Count', 'y': 'Venue Type'},
            color_discrete_sequence=["#FF6500"]
        )
        fig1.update_layout(height=320, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig1, use_container_width=True)

        # Media Owner Distribution
        owner_counts = filtered_df['Media owner'].value_counts().head(5)
        fig2 = px.pie(
            values=owner_counts.values,
            names=owner_counts.index,
            title='Top 5 Media Owners',
            color_discrete_sequence=brand_seq
        )
        fig2.update_layout(height=320, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)

        # Top Regions (by Site region/state)
        region_counts = (
            filtered_df['Site region (state)']
            .fillna('Unknown')
            .value_counts()
            .head(10)
        )
        fig3 = px.bar(
            x=region_counts.index,
            y=region_counts.values,
            title='Top 10 Regions',
            labels={'x': 'Region', 'y': 'Count'},
            color_discrete_sequence=["#2B0030"]
        )
        fig3.update_layout(height=320, showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Adjust filters to see analytics.")

with tabs[1]:
    # Detailed data table and export
    display_columns = [
        'Screen name', 'Venue type', 'Media owner', 'Site location (city)', 
        'Site region (state)', 'Country', 'Dimensions (W x H)', 'Orientation',
        'Allow Image', 'Allow Video', 'Spot length'
    ]
    st.dataframe(
        filtered_df[display_columns].reset_index(drop=True),
        use_container_width=True,
        height=420
    )
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_dooh_screens.csv",
        mime="text/csv",
    )
 

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>DOOH Screens Dashboard | Interactive Screen Location Analytics</p>
        <p style="font-size: 12px;">MiQ Digital</p>
    </div>
    """, unsafe_allow_html=True)
