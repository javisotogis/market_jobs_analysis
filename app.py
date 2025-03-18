import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Load the data
df = pd.read_csv(r"tmp_outputs/df_lat_long.csv")

# Ensure expirationDate column is a string
df["expirationDate"] = df["expirationDate"].astype(str)

# Define Streamlit layout settings (Wider Page)
st.set_page_config(layout="wide")

# Define job types and locations (Excluding Remote)
job_types = ["GIS", "Data Analyst"]
locations = ["England", "Scotland", "Wales", "N. Ireland"]

# Rename "Northern Ireland" to "N. Ireland" in the DataFrame
df["location"] = df["location"].replace({"Northern Ireland": "N. Ireland"})

# Aggregate job statistics
aggregated_df = df.groupby(["job_position", "location"]).agg({
    "minimumSalary": "mean",
    "maximumSalary": "mean"
}).reset_index()

# Count the number of jobs per category
aggregated_df["number_of_jobs"] = df.groupby(["job_position", "location"]).size().values

# Compute UK-wide insights per job position
uk_wide_stats = df.groupby("job_position").agg({
    "minimumSalary": "mean",
    "maximumSalary": "mean"
}).reset_index()

# Add total number of jobs for each job position
uk_wide_stats["total_jobs"] = df.groupby("job_position").size().values

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Job Statistics", "Job Map"])

# === JOB STATISTICS PAGE === #
if page == "Job Statistics":
    st.title("Comparing GIS and Data Analyst Jobs in the UK")

    st.markdown("""
---
📢 **Disclaimer:**  
The job data presented in this dashboard is sourced from the **Reed Jobs website**.  
This data is **not updated in real-time** and represents a snapshot of job listings at the time of data collection.
""")


    # ===== UK-WIDE INSIGHTS PER JOB POSITION ===== #
    st.subheader("UK-Wide Insights for GIS and Data Analyst Jobs")

    # Create two cards for each job position (GIS & Data Analyst)
    uk_insight_cols = st.columns(2)  # Two cards in one row

    for i, job in enumerate(job_types):
        job_data = uk_wide_stats[uk_wide_stats["job_position"].str.contains(job, case=False, na=False)]
        
        if not job_data.empty:
            avg_min_salary = f"£{job_data['minimumSalary'].values[0]:,.2f}"
            avg_max_salary = f"£{job_data['maximumSalary'].values[0]:,.2f}"
            total_jobs = job_data["total_jobs"].values[0]
        else:
            avg_min_salary = "No data available"
            avg_max_salary = "No data available"
            total_jobs = 0

        with uk_insight_cols[i]:
            st.markdown(f"""
            <div style="padding:15px; border-radius:10px; background-color:#f8f9fa; 
                        box-shadow:2px 2px 10px rgba(0,0,0,0.1); text-align:center;">
                <h3 style="color:#007bff;">{job} Jobs (UK)</h3>
                <p style="font-size:16px;"><strong>Avg Min Salary:</strong> {avg_min_salary}</p>
                <p style="font-size:16px;"><strong>Avg Max Salary:</strong> {avg_max_salary}</p>
                <p style="font-size:16px;"><strong>Total Jobs:</strong> {total_jobs}</p>
            </div>
            """, unsafe_allow_html=True)

    # ===== JOB-SPECIFIC NATION CARDS ===== #
    def display_cards(job_type):
        st.subheader(f"{job_type} Jobs")

        # Filter data for the job type
        filtered_df = aggregated_df[aggregated_df["job_position"].str.contains(job_type, case=False, na=False)]

        # Create columns for the four nations
        cols = st.columns([1.5, 1.5, 1.5, 1.5])

        for i, location in enumerate(locations):
            location_data = filtered_df[filtered_df["location"] == location]

            if not location_data.empty:
                row = location_data.iloc[0]
                min_salary = f"£{row['minimumSalary']:,.2f}" if not pd.isna(row['minimumSalary']) else "No data available"
                max_salary = f"£{row['maximumSalary']:,.2f}" if not pd.isna(row['maximumSalary']) else "No data available"
                num_jobs = row["number_of_jobs"]
            else:
                min_salary = "No data available"
                max_salary = "No data available"
                num_jobs = 0

            # Display the card
            with cols[i]:
                st.markdown(f"""
                <div style="padding:12px; border-radius:10px; background-color:#f8f9fa; 
                            box-shadow:2px 2px 10px rgba(0,0,0,0.1); text-align:center;
                            width: 100%; margin: auto;">
                    <h4 style="color:#007bff; font-size:16px;">{location}</h4>
                    <p style="font-size:14px;"><strong>Type:</strong> {job_type}</p>
                    <p style="font-size:14px;"><strong>Avg Min Salary:</strong> {min_salary}</p>
                    <p style="font-size:14px;"><strong>Avg Max Salary:</strong> {max_salary}</p>
                    <p style="font-size:14px;"><strong>Number of Jobs:</strong> {num_jobs}</p>
                </div>
                """, unsafe_allow_html=True)

    # Display GIS Jobs in the first row
    display_cards("GIS")

    # Display Data Analyst Jobs in the second row
    display_cards("Data Analyst")

    # === PLOTLY VISUALIZATIONS === #
    st.subheader("Salary Distribution by Job Position")

    # Interactive Bar Chart for Minimum Salary
    fig_min = px.bar(
        aggregated_df,
        x="job_position",
        y="minimumSalary",
        color="location",
        title="Average Minimum Salary by Job Position",
        labels={"minimumSalary": "Avg Min Salary (£)"},
        barmode="group"
    )
    st.plotly_chart(fig_min, use_container_width=True)

    # Interactive Bar Chart for Maximum Salary
    fig_max = px.bar(
        aggregated_df,
        x="job_position",
        y="maximumSalary",
        color="location",
        title="Average Maximum Salary by Job Position",
        labels={"maximumSalary": "Avg Max Salary (£)"},
        barmode="group"
    )
    st.plotly_chart(fig_max, use_container_width=True)

# === JOB MAP PAGE === #
elif page == "Job Map":
    st.title("Job Locations Map")

    # Drop rows with missing latitude or longitude
    df_clean = df.dropna(subset=["latitude", "longitude"]).copy()

    if df_clean.empty:
        st.warning("No job locations available to display on the map.")
    else:
        # Create a Folium Map centered over the UK
        m = folium.Map(location=[54.0, -2.0], zoom_start=6)

        # Use MarkerCluster for better clustering & popups
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df_clean.iterrows():
            lat, lon = row["latitude"], row["longitude"]

            # Create popup with job details
            popup_text = f"""
                <b>Job Position:</b> {row['job_position']}<br>
                <b>Location:</b> {row['location']}<br>
                <b>Employer:</b> {row['employerName']}<br>
                <b>Min Salary:</b> £{row['minimumSalary']:,.2f}<br>
                <b>Max Salary:</b> £{row['maximumSalary']:,.2f}<br>
                <b>Expiration Date:</b> {row['expirationDate']}<br>
            """

            # Add markers
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color="blue")
            ).add_to(marker_cluster)

        # Show the map
        folium_static(m)
