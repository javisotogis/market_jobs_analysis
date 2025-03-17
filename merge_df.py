import pandas as pd
import glob
import os

def load_and_concat_job_data(directory: str, file_pattern: str = "*.csv"):
    """
    Reads all CSV files in the given directory matching the pattern,
    extracts job position and location from filenames,
    and concatenates them into a single DataFrame with error handling.
    
    Args:
        directory (str): The directory containing the CSV files.
        file_pattern (str, optional): The pattern for CSV files. Default is "*.csv".

    Returns:
        pd.DataFrame: Concatenated DataFrame with added job_position and location columns.
    """
    files = glob.glob(os.path.join(directory, file_pattern))
    
    all_dataframes = []
    
    for file in files:
        try:
            # Extract job position and location from filename
            filename = os.path.basename(file)
            parts = filename.replace(".csv", "").split("__")
            if len(parts) != 2:
                print(f"Skipping file {filename}: incorrect filename format")
                continue
            job_position, location = parts
            
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Add extracted job position and location as columns
            df["job_position"] = job_position
            df["location"] = location
            
            all_dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Concatenate all DataFrames if there is data
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        return final_df
    else:
        print("No valid CSV files were processed.")
        return pd.DataFrame()  # Return an empty DataFrame if no files were processed



