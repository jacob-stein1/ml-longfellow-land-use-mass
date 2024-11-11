import os
import re


def retrieve_csv(path):
    #open file
    with open(path, "r", encoding="utf-8") as file:
        csv_content = file.read()

    #create pattern
    pattern = r",,\"(.*?)\""

    #filter by pattern
    matches = re.findall(pattern, csv_content)

    #filter duplicates
    matches = set(matches)
    
    return matches

    
