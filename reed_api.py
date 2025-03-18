import requests
import base64
import csv
import time  # To avoid too many rapid requests
from dotenv import load_dotenv
import os

load_dotenv()
# Replace with your real API Key
API_KEY = os.getenv("API_KEY")
# Replace with your real API Key
time_sleep = 0.25

def get_reed_jobs(job_title, location, total_results=10000, results_per_page=100):
    url = "https://www.reed.co.uk/api/1.0/search"

    # Authentication with API Key in Base64
    auth_value = base64.b64encode(f"{API_KEY}:".encode()).decode()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {auth_value}"
    }

    all_jobs = []  # List to store all retrieved jobs

    # Loop to fetch multiple pages of results
    for skip in range(0, total_results, results_per_page):
        params = {
            "keywords": job_title,
            "locationName": location,
            "resultsToTake": results_per_page,
            "resultsToSkip": skip
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            jobs = response.json().get("results", [])
            if not jobs:
                break  # If there are no more jobs, exit the loop

            all_jobs.extend(jobs)  # Add new jobs to the list
            print(f"Retrieved {len(jobs)} jobs (Total: {len(all_jobs)})")

            time.sleep(time_sleep)  # Brief wait to avoid overloading the API

        else:
            print("Error:", response.status_code, response.text)
            break  # Exit if there is an error

    if all_jobs:
        # Get all unique keys from jobs for the CSV
        all_keys = set()
        for job in all_jobs:
            all_keys.update(job.keys())

        # Save the data to a CSV file
        filename = f"{job_title}__{location}.csv"
        with open(r"tmp_outputs/" + filename , mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(all_keys))
            writer.writeheader()
            writer.writerows(all_jobs)

        print(f"✅ Data saved in {filename} ({len(all_jobs)} jobs)")

    else:
        print("⚠ No jobs found.")

# 📌 Example: Retrieve up to 500 Data Analyst jobs in Leeds





 