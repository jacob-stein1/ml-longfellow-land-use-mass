import os
import pandas as pd
import sys
sys.path.append('../deed_preprocessing')
from preprocessor import preprocess_text

# Define the directory paths
script_dir = os.path.dirname(os.path.abspath(__file__))
racist_deeds_dir = os.path.join(script_dir, "racist_deeds_text")
extracted_info_dir = os.path.join(script_dir, "extracted_info")
output_file = os.path.join(extracted_info_dir, "extracted_names_locations.xlsx")

# Ensure the extracted_info directory exists
os.makedirs(extracted_info_dir, exist_ok=True)

def extract_names_and_locations():
    # Initialize a list to store data for each file
    data = []

    # Process each file
    for file in os.listdir(racist_deeds_dir):
        if file.endswith(".txt"):
            with open(os.path.join(racist_deeds_dir, file), 'r', encoding='utf-8') as f:
                text = f.read()
                processed = preprocess_text(text)

                # Extract names and locations
                names = processed.get("names", [])
                locations = processed.get("locations", [])

                # Append the data for this file as a row in the list
                data.append({
                    "File Name": file,
                    "Names": ", ".join(names),
                    "Locations": ", ".join(locations)
                })

    # Convert the data into a DataFrame and save to Excel in the extracted_info directory
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

# Run the function to save the output to an Excel file in the extracted_info directory
extract_names_and_locations()
