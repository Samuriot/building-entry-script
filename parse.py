from typing import List
from collections import defaultdict
from datetime import datetime
import csv
import os
import sys
import re
from pathlib import Path

def import_dataset(filename: str) -> dict[str, List]:
    locations = defaultdict(list)
    with open("dataset.csv", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:            
            if not any((value or "").strip() for value in row.values()):
                continue
            row.pop("", None)
            date = row.get('Date', '')
            time = row.get('Time', '')
            
            # Convert date to YYYY-MM-DD format
            date_formatted = date
            for date_fmt in ['%m/%d/%Y', '%m/%d/%y']:
                try:
                    date_obj = datetime.strptime(date, date_fmt)
                    date_formatted = date_obj.strftime('%Y-%m-%d')
                    break
                except:
                    continue
            
            # Convert time from 12-hour to 24-hour format
            try:
                time_obj = datetime.strptime(time, '%I:%M %p')
                time_24hr = time_obj.strftime('%H:%M')
            except:
                time_24hr = time
            
            datetime_str = f"{date_formatted} {time_24hr}"
            
            for item in row:
                if item in ['Time', 'Date']:
                    continue
                count_value = row[item].strip() if row[item] else "-1"
                entry_data = {
                    'datetime': datetime_str,
                    'count': int(count_value) if count_value else 0
                }
                locations[item].append(entry_data)
    
    locations_dict: dict[str, List] = {location: entries for location, entries in locations.items()}
    return locations_dict


def validate_data(locations_dict):    
    # Regex pattern for YYYY-MM-DD format
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}')
    
    for location, entries in locations_dict.items():
        for entry in entries:
            # Validate date format (YYYY-MM-DD)
            datetime_str = entry.get('datetime', '')
            if not date_pattern.match(datetime_str):
                # Try to fix common date formats
                try:
                    # Extract date part before the time
                    parts = datetime_str.split(' ')
                    if len(parts) >= 2:
                        date_part = parts[0]
                        time_part = ' '.join(parts[1:])
                        
                        # Try various date formats
                        for fmt in ['%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%d/%m/%y', '%Y/%m/%d']:
                            try:
                                date_obj = datetime.strptime(date_part, fmt)
                                entry['datetime'] = f"{date_obj.strftime('%Y-%m-%d')} {time_part}"
                                break
                            except:
                                continue
                except:
                    pass
            
            # Validate count is not negative
            if entry.get('count', 0) < 0:
                entry['count'] = 0
    
    return locations_dict


def export_to_csv(locations_dict):
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    for location, entries in locations_dict.items():
        # Create a safe filename from location name
        filename = f"data/{location.replace(' ', '_').replace('/', '_')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['date', 'gate_start'])
            
            # Write data rows
            for entry in entries:
                writer.writerow([entry['datetime'], entry['count']])
        
        print(f"Exported {filename}")


def main():
    if len(sys.argv) < 2:
        print("Exiting program, provide the csv file name to parse - E.G. python3 parse.py <FILE_NAME>.csv")
        return
    file_path = Path(sys.argv[1])
    if file_path.suffix != ".csv":
        print("Exiting program, file provided is not a .csv - E.G. python3 parse.py <FILE_NAME>.csv")
        return
    formatted_dataset = import_dataset(file_path.name)
    validated_dataset = validate_data(formatted_dataset)
    export_to_csv(validated_dataset)

if __name__ == '__main__':
    main()
