from src.form_filler import FormFiller

import csv
import os

def get_output_file_name(player_data):
    player_name = player_data['playersname'].replace(' ','-')
    return os.path.join(f"{player_name}.pdf")

def fill_forms(csv_file, output_dir='.'):
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    ff = FormFiller()
    for row in rows:
        output_file_name = os.path.join(output_dir, row['batch'], get_output_file_name(row))
        os.makedirs(os.path.dirname(output_file_name), exist_ok=True)
        ff.fill(row, output_file_name)
        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fill the provided details in the consent forms.")
    parser.add_argument("--csv", required=True, help="path of the csv file containing the players data")
    parser.add_argument("--dest", required=False, help="path of the destination folder to save the filled forms")
    
    args = parser.parse_args()
    CSV_PATH = args.csv
    DEST_DIR = args.dest or './FilledForms'
    fill_forms(CSV_PATH, DEST_DIR)
