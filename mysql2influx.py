import csv
import requests
from datetime import datetime

# InfluxDB server configuration
influxdb_url = 'http://ipaddress:8086/api/v2/write?org=organisation&bucket=bucket&precision=s'
influxdb_token = 'token'  # Add your InfluxDB token here
headers = {
    'Authorization': f'Token {influxdb_token}',
    'Content-Type': 'text/plain'
}


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
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())


# Function to escape spaces in tags or field values
def escape_spaces(value):
    return value.replace(" ", "\\ ")


# Convert a single dataset to InfluxDB line protocol format
def convert_to_line_protocol(data):
    measurement = data["measurement"]

    # Escape spaces in tag values
    tags = ','.join([f'{k}={escape_spaces(v)}' for k, v in data["tags"].items()])

    # Escape spaces in field values if necessary (usually not needed for numeric fields)
    fields = ','.join([f'{k}={v}' for k, v in data["fields"].items()])

    timestamp = data["timestamp"]

    line_protocol = f'{measurement},{tags} {fields} {timestamp}'
    return line_protocol


# Define input file path
input_csv = 'sample.csv'  # Path to your CSV file

# Define the structure of the final data
line_protocol_data = []

# Open the CSV file and read the first 20 lines
with open(input_csv, mode='r') as file:
    reader = csv.DictReader(file)

    # Track the number of lines processed
    line_count = 0
    for row in reader:
        if line_count >= 20:
            pass
            #break  # Stop after processing 20 lines

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
            line_protocol = convert_to_line_protocol(data_entry)
            line_protocol_data.append(line_protocol)

        line_count += 1


# Send the data to InfluxDB
def upload_to_influxdb(line_protocol_data):
    data = '\n'.join(line_protocol_data)  # Join all line protocol entries
    response = requests.post(influxdb_url, headers=headers, data=data)

    if response.status_code == 204:
        print("Data successfully uploaded to InfluxDB")
    else:
        print(f"Failed to upload data. Status code: {response.status_code}")
        print(f"Response: {response.text}")


# Upload the line protocol data to InfluxDB
upload_to_influxdb(line_protocol_data)