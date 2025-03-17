"""
main.py - Entry point for the application
"""

# Import necessary modules
import sys
import time
from reed_api import get_reed_jobs
from merge_df import load_and_concat_job_data
from get_lat_long import add_lat_long


# Main execution
if __name__ == "__main__":
    # Optionally handle command-line arguments
    now = time.time()
    args = sys.argv[1:]
    
    # Call main functions or orchestrate execution
    print("Get jobs from reed website...")
    for job in ["data analyst", "GIS"]:
        for location in ["England", "Scotland", "Wales", "Northern Ireland", "remote"]:
            get_reed_jobs(job, location, total_results=10000, results_per_page=100)
    print("Concate all jobs...")
    df = load_and_concat_job_data("tmp_outputs")
    print("Get lat and long from dataframes...")
    df = add_lat_long(df, "locationName")
    print(df.head())
    df.to_csv("tmp_outputs/df_lat_long.csv", index=False)
    now2 = time.time()
    print(f"Time taken: {now2 - now:.2f} seconds")
