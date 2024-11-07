import os
import pandas as pd
from pathlib import Path
import sys
sys.path.append('../deed_preprocessing')
from preprocessor import preprocess_text
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def preprocess_deeds():
    sys.path.append('../deed_preprocessing')
    from preprocessor import preprocess_text

    racist_dir = Path('./racist_deeds_text')
    non_racist_dir = Path('./non_racist_deeds_text')

    all_data = pd.DataFrame()

    racist_count = 0
    non_racist_count = 0

    def process_directory(directory, is_racist_label):
        nonlocal all_data, racist_count, non_racist_count
        for file in directory.iterdir():
            if file.is_file() and file.suffix == '.txt':
                with file.open('r', encoding='utf-8') as f:
                    text = f.read()
                    processed_text = preprocess_text(text)

                    df = pd.DataFrame([processed_text])
                    df['is_racist'] = is_racist_label

                    all_data = pd.concat([all_data, df], ignore_index=True)

                if is_racist_label == 1:
                    racist_count += 1
                else:
                    non_racist_count += 1

    process_directory(racist_dir, 1)
    process_directory(non_racist_dir, 0)

    print(f"Number of racist text files read: {racist_count}")
    print(f"Number of non-racist text files read: {non_racist_count}")

    return all_data

if __name__ == "__main__":
    preprocessed_data = preprocess_deeds()
    preprocessed_data.to_pickle('preprocessed_deeds.pkl')
