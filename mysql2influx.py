import csv
import json
from datetime import datetime

# Function to safely convert values to float and handle "NULL"
def safe_float(value):
    try:
        if value == "NULL":
            return None
        return float(value)
    except ValueError:
        return None

# Function to convert "timestamp_utc" to Unix timestamp (in seconds)
def convert_to_unix_timestamp(timestamp_str):
    # Parse the timestamp from the string format
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    # Convert to Unix timestamp in seconds
    return int(dt.timestamp())

# Define input and output file paths
input_csv = 'sample.csv'  # Path to your CSV file
output_json = 'output.json'  # Path where the JSON will be saved

# Define the structure of the final data
portfolio_data = []

# Open the CSV file and read the first 20 lines
with open(input_csv, mode='r') as file:
    reader = csv.DictReader(file)

    # Track the number of lines processed
    line_count = 0
    for row in reader:
        if line_count >= 2:
            break  # Stop after processing 20 lines

        # Generate the timestamp in seconds
        timestamp = convert_to_unix_timestamp(row["timestamp_utc"])

        # Construct the measurement object and exclude "NULL" fields
        fields = {
            "stk": safe_float(row["stk"]),
            "einstandskurs": safe_float(row["einstandskurs"]),
            "letzter_kurs": safe_float(row["letzter_kurs"]),
            "aktueller_wert": safe_float(row["aktueller_wert"]),
            "einstandswert": safe_float(row["einstandswert"]),
            "entwicklung_abs": safe_float(row["entwicklung_abs"]),
            "entwicklung_perc": safe_float(row["entwicklung_perc"]),
            "vortag": safe_float(row["vortag"]),
            "vortag_perc": safe_float(row["vortag_perc"])
        }

        # Remove None values (those that were originally "NULL")
        fields = {k: v for k, v in fields.items() if v is not None}

        # Create the data entry only if there are valid fields
        if fields:
            data_entry = {
                "measurement": "portfolio_position",
                "fields": fields,
                "tags": {
                    "bezeichnung": row["bezeichnung"],
                    "isin": row["isin"],
                    "wkn": row["wkn"],
                    "lagerst": row["lagersts"],
                    "boerse": row["boerse"]
                },
                "timestamp": timestamp  # Add the Unix timestamp
            }
            portfolio_data.append(data_entry)

        line_count += 1

# Save the data to a JSON file
with open(output_json, 'w') as json_file:
    json.dump(portfolio_data, json_file, indent=4)

print(f"Data successfully saved to {output_json}")