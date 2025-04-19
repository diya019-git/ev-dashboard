import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title="EV Market Intelligence Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stSelectbox, .stMultiselect, .stSlider {
        padding: 0.5rem;
    }
    .css-1aumxhk {
        background-color: #ffffff;
        background-image: none;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .header-text {
        color: #2c3e50;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Load dataset with caching
@st.cache_data
def load_data():
    return pd.read_csv("Electric_Vehicle_Population_Data.csv")

df = load_data()

@st.cache_data
def load_data():
    df = pd.read_csv("Electric_Vehicle_Population_Data.csv")
    
    # Clean numeric columns
    df["Electric Range"] = pd.to_numeric(df["Electric Range"], errors='coerce')
    df["Base MSRP"] = pd.to_numeric(df["Base MSRP"], errors='coerce')
    
    # Fill NA/NaN values if needed
    df["Electric Range"] = df["Electric Range"].fillna(0)
    df["Base MSRP"] = df["Base MSRP"].fillna(0)
    
    return df

df = load_data()

# Sidebar with enhanced filters
with st.sidebar:
    # Logo and title
    st.image("https://cdn-icons-png.flaticon.com/512/2252/2252691.png", width=80)
    st.title("🔍 EV Market Explorer")
    st.markdown("Customize your analysis using the filters below:")
    
    # Enhanced filters
    with st.expander("🚗 Vehicle Filters", expanded=True):
        make_filter = st.multiselect(
            "Select Manufacturer(s)",
            options=sorted(df["Make"].unique()),
            default=["TESLA", "FORD", "CHEVROLET", "NISSAN", "BMW"]
        )
        model_filter = st.multiselect(
            "Select Model(s)",
            options=sorted(df["Model"].unique()) if not make_filter else sorted(df[df["Make"].isin(make_filter)]["Model"].unique())
        )
        year_filter = st.slider(
            "Model Year Range",
            int(df["Model Year"].min()),
            int(df["Model Year"].max()),
            (2015, 2025)
        )
        ev_type_filter = st.multiselect(
            "EV Type",
            options=df["Electric Vehicle Type"].unique(),
            default=df["Electric Vehicle Type"].unique()
        )
    
    with st.expander("📍 Location Filters"):
        county_filter = st.multiselect(
            "Select County",
            options=sorted(df["County"].dropna().unique())
        )
        city_filter = st.multiselect(
            "Select City",
            options=sorted(df["City"].dropna().unique())
        )
    
    with st.expander("⚡ Performance Filters"):
        range_filter = st.slider(
            "Electric Range (miles)",
            int(df["Electric Range"].min()),
            int(df["Electric Range"].max()),
            (0, 400)
        )
        msrp_filter = st.slider(
            "Base MSRP ($)",
            int(df["Base MSRP"].min()),
            int(df["Base MSRP"].max()),
            (0, 150000)
        )

# Apply filters with proper parenthesis matching
filter_conditions = [
    (df["Make"].isin(make_filter)) if make_filter else True,
    (df["Model"].isin(model_filter)) if model_filter else True,
    (df["Model Year"].between(*year_filter)),
    (df["Electric Vehicle Type"].isin(ev_type_filter)),
    (df["County"].isin(county_filter)) if county_filter else True,
    (df["City"].isin(city_filter)) if city_filter else True,
    (df["Electric Range"].between(*range_filter)),
    (df["Base MSRP"].between(*msrp_filter))
]

# Combine all conditions
final_condition = pd.Series(True, index=df.index)
for condition in filter_conditions:
    final_condition &= condition

df_filtered = df[final_condition]

# Dashboard Header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176272.png", width=120)
with col2:
    st.title("Electric Vehicle Market Intelligence")
    st.markdown("""
    <div style='color:#7f8c8d; font-size: 16px;'>
    Comprehensive analysis of electric vehicle adoption, market trends, and performance metrics
    </div>
    """, unsafe_allow_html=True)

# KPI Metrics - SAFE VERSION
col1, col2, col3, col4 = st.columns(4)

# Total EVs (always works)
col1.metric("Total EVs", f"{len(df_filtered):,}")

# Unique Makes (always works)
col2.metric("Unique Makes", df_filtered["Make"].nunique())

# Average Range (with error handling)
try:
    avg_range = int(pd.to_numeric(df_filtered["Electric Range"], errors='coerce').mean())
except:
    avg_range = 0
col3.metric("Avg Range (mi)", f"{avg_range}")

# Average MSRP (with error handling)
try:
    avg_msrp = int(pd.to_numeric(df_filtered["Base MSRP"], errors='coerce').mean())
except:
    avg_msrp = 0
col4.metric("Avg MSRP ($)", f"{avg_msrp:,}")
# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Trends", "📍 Geographic Analysis", "⚡ Performance Metrics", "🔍 Raw Data"])

with tab1:
    st.markdown("### 🚗 Market Share Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Top 10 Manufacturers")
        top_makes = df_filtered["Make"].value_counts().nlargest(10).reset_index()
        top_makes.columns = ["Make", "Count"]
        fig = px.bar(top_makes, x="Make", y="Count", color="Make",
                    title="", template="plotly_white")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### EV Adoption Timeline")
        year_trend = df_filtered["Model Year"].value_counts().sort_index().reset_index()
        year_trend.columns = ["Year", "Count"]
        fig = px.area(year_trend, x="Year", y="Count", markers=True,
                     title="", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("##### Vehicle Type Distribution")
    type_dist = df_filtered["Electric Vehicle Type"].value_counts().reset_index()
    type_dist.columns = ["Type", "Count"]
    fig = px.pie(type_dist, names="Type", values="Count", hole=0.3,
                color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("### 🌎 Geographic Distribution")
    
    if "County" in df_filtered.columns and "City" in df_filtered.columns:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Top Counties")
            county_counts = df_filtered["County"].value_counts().nlargest(10).reset_index()
            county_counts.columns = ["County", "Count"]
            fig = px.bar(county_counts, x="County", y="Count", color="County",
                        title="", template="plotly_white")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Top Cities")
            city_counts = df_filtered["City"].value_counts().nlargest(10).reset_index()
            city_counts.columns = ["City", "Count"]
            fig = px.bar(city_counts, x="City", y="Count", color="City",
                        title="", template="plotly_white")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # First ensure you have latitude/longitude data
        if "Latitude" in df_filtered.columns and "Longitude" in df_filtered.columns:
            st.markdown("##### Geographic Heatmap")
            fig = px.density_mapbox(
                df_filtered,
                lat="Latitude",
                lon="Longitude",
                z="Electric Range",  # Or any numeric column you want to visualize
                radius=20,
                zoom=5,
                mapbox_style="stamen-terrain",
                hover_data=["Make", "Model", "County", "City"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Latitude/Longitude data not available - cannot render map")
    else:
        st.warning("Geographic data not available in the filtered dataset")

with tab3:
    st.markdown("### ⚡ Performance Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Range Distribution")
        fig = px.histogram(df_filtered, x="Electric Range", nbins=20,
                          title="", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Price Distribution")
        fig = px.box(df_filtered, y="Base MSRP", points="all",
                    title="", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("##### Range vs. Price Correlation")
    scatter = px.scatter(
        df_filtered, x="Base MSRP", y="Electric Range",
        color="Make", hover_data=["Model", "Model Year"],
        trendline="lowess", template="plotly_white"
    )
    st.plotly_chart(scatter, use_container_width=True)

with tab4:
    st.markdown("### 🔍 Detailed EV Data")
    st.dataframe(df_filtered.sort_values("Model Year", ascending=False))
    
    # Enhanced data export
    st.markdown("##### Export Options")
    export_format = st.radio("Select export format:", ("CSV", "Excel", "JSON"))
    
    if export_format == "CSV":
        buffer = io.StringIO()
        df_filtered.to_csv(buffer, index=False)
        st.download_button(
            "📥 Download as CSV",
            data=buffer.getvalue(),
            file_name="ev_data_export.csv",
            mime="text/csv"
        )
    elif export_format == "Excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filtered.to_excel(writer, index=False)
        st.download_button(
            "📥 Download as Excel",
            data=buffer,
            file_name="ev_data_export.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.download_button(
            "📥 Download as JSON",
            data=df_filtered.to_json(orient="records"),
            file_name="ev_data_export.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 14px;'>
    <p>Electric Vehicle Market Intelligence Dashboard | Data updated: {}</p>
    <p>© 2025 Diya Gupta </p>
</div>
""".format(pd.to_datetime('today').strftime('%Y-%m-%d')), unsafe_allow_html=True)