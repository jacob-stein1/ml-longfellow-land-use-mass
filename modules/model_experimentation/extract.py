import os
from preprocessor import preprocess_text

# Define absolute paths to avoid FileNotFoundError
script_dir = os.path.dirname(os.path.abspath(__file__))
racist_deeds_dir = os.path.join(script_dir, "racist_deeds_text")
output_file = os.path.join(script_dir, "extracted_names_locations.txt")

def extract_names_and_locations():
    # Open the output file to write the extracted information
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for file in os.listdir(racist_deeds_dir):
            if file.endswith(".txt"):
                with open(os.path.join(racist_deeds_dir, file), 'r', encoding='utf-8') as f:
                    text = f.read()
                    processed = preprocess_text(text)

                    # Extract names and locations
                    names = processed.get("names", [])
                    locations = processed.get("locations", [])

                    # Write to output file
                    out_file.write(f"File: {file}\n")
                    out_file.write(f"Names: {', '.join(names)}\n")
                    out_file.write(f"Locations: {', '.join(locations)}\n")
                    out_file.write("\n" + "-"*40 + "\n")

# Run the function to save the output to a file
extract_names_and_locations()
