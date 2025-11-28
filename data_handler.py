import csv
import os

DATA_FILE = "transactions.csv"

def debug_csv():
    if not os.path.isfile(DATA_FILE):
        print("File not found.")
        return

    print(f"Reading {DATA_FILE}...")
    try:
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"Fieldnames: {reader.fieldnames}")
            for i, row in enumerate(reader):
                print(f"Row {i}: {row}")
                try:
                    t = row["Type"]
                except KeyError as e:
                    print(f"KeyError at row {i}: {e}. Keys found: {list(row.keys())}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    debug_csv()