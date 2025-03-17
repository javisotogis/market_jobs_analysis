import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
import seaborn as sns
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Load the data
df = pd.read_csv(r"tmp_outputs/df_lat_long.csv")

# Ensure expirationDate column is a string (in case it's read as a float)
df["expirationDate"] = df["expirationDate"].astype(str)

# Generate dynamic colors based on unique locations
unique_locations = df["location"].unique()
color_palette = ["blue", "green", "red", "purple", "orange", "cyan", "magenta", "yellow"]

# Assign each location a unique color
location_colors = {loc: color_palette[i % len(color_palette)] for i, loc in enumerate(unique_locations)}

# Create a new color column in the DataFrame
df["color"] = df["location"].map(location_colors)

# Streamlit Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Job Statistics", "Job Map"])

# === JOB STATISTICS PAGE === #
if page == "Job Statistics":
    st.title("Job Market Dashboard")

    # Aggregate the data
    aggregated_df = df.groupby(["job_position", "location"]).agg({
        "minimumSalary": "mean",
        "maximumSalary": "mean"
    }).reset_index()

    # Count number of jobs per category
    aggregated_df["number_of_jobs"] = df.groupby(["job_position", "location"]).size().values

    # Display Cards
    st.subheader("Job Statistics Overview")
    for index, row in aggregated_df.iterrows():
        with st.container():
            st.markdown(f"""
            <div style="padding:10px; border-radius:10px; background-color:#f8f9fa; box-shadow:2px 2px 10px rgba(0,0,0,0.1); margin-bottom:10px;">
                <h3>{row['job_position']} - {row['location']}</h3>
                <p><strong>Avg Min Salary:</strong> ${row['minimumSalary']:,.2f}</p>
                <p><strong>Avg Max Salary:</strong> ${row['maximumSalary']:,.2f}</p>
                <p><strong>Number of Jobs:</strong> {row['number_of_jobs']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Visualizations
    st.subheader("Salary Distribution by Job Position")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=aggregated_df, x="job_position", y="minimumSalary", hue="location", ax=ax)
    ax.set_title("Average Minimum Salary by Job Position")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=aggregated_df, x="job_position", y="maximumSalary", hue="location", ax=ax)
    ax.set_title("Average Maximum Salary by Job Position")
    st.pyplot(fig)

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
            job_type = row["job_position"]
            color = row["color"]
            lat, lon = row["latitude"], row["longitude"]

            # Create popup with full job details
            popup_text = f"""
                <b>Job Position:</b> {row['job_position']}<br>
                <b>Location:</b> {row['location']}<br>
                <b>Employer:</b> {row['employerName']}<br>
                <b>Min Salary:</b> £{row['minimumSalary']:,.2f}<br>
                <b>Max Salary:</b> £{row['maximumSalary']:,.2f}<br>
                <b>Expiration Date:</b> {row['expirationDate']}<br>
            """

            # Add individual markers with popups inside MarkerCluster
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(marker_cluster)

        # Show the map
        folium_static(m)
