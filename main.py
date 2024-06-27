import os
import json
import zipfile
import pandas as pd
from geopy.distance import geodesic
import holidays
from collections import defaultdict
import datetime
from geopy.distance import geodesic
import holidays
from geopy.distance import great_circle
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict

def extract_zip_files(folder_path):
    """
    Extract all zip files in the given folder.
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".zip"):
            zip_path = os.path.join(folder_path, file_name)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)

def filter_json_files(folder_path, relevant_lines):
    """
    Recursively filter JSON files in the given folder and its subdirectories,
    keeping only records with relevant lines.
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if not file_name.endswith(".json"):
                continue
            
            file_path = os.path.join(root, file_name)
            
            with open(file_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    continue
                
            filtered_data = [record for record in data if record.get('linha') in relevant_lines]
            
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(filtered_data, json_file, ensure_ascii=False, indent=4)

def group_sequence_json_files(folder_path):
    """
    Group JSON files by 'linha' and sequence them by 'datahora', then rewrite the JSON files.
    
    Args:
    - folder_path (str): Path to the folder containing JSON files.
    """
    # Traverse the folder and subfolders to process all JSON files
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if not file_name.endswith(".json"):
                continue
            
            file_path = os.path.join(root, file_name)
            output_file_path = os.path.join(root, f"{os.path.splitext(file_name)[0]}_sorted.json")
            
            data_by_line = defaultdict(list)
            
            with open(file_path, 'r', encoding='utf-8') as json_file:
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    continue
            
            for record in data:
                linha = record.get('linha')
                datahora = record.get('datahora')
                
                if linha and datahora:
                    data_by_line[linha].append(record)
            
            # Sort records by 'datahora' within each 'linha'
            for linha, records in data_by_line.items():
                data_by_line[linha] = sorted(records, key=lambda x: x['datahora'])
            
            # Write sorted records back to a new JSON file
            with open(output_file_path, 'w', encoding='utf-8') as json_file:
                for linha, records in data_by_line.items():
                    json.dump(records, json_file, ensure_ascii=False, indent=4)
                    json_file.write('\n')

                
def calculate_velocity(lat1, lon1, lat2, lon2, time_diff_seconds):
    """
    Calculate real velocity between two geographic points.
    
    Args:
    - lat1, lon1: Latitude and longitude of the first point (as strings).
    - lat2, lon2: Latitude and longitude of the second point (as strings).
    - time_diff_seconds: Time difference between points in seconds (as float).
    
    Returns:
    - Real velocity in km/h (as float).
    """
    try:
        point1 = (float(lat1.replace(',', '.')), float(lon1.replace(',', '.')))
        point2 = (float(lat2.replace(',', '.')), float(lon2.replace(',', '.')))
        
        distance_km = geodesic(point1, point2).kilometers
        velocity_kmh = (distance_km / (time_diff_seconds / 3600)) if time_diff_seconds > 0 else 0.0
        
        return velocity_kmh
    except ValueError:
        return 0.0
    except Exception as e:
        print(f"Error calculating velocity: {e}")
        return 0.0

def load_json_file(file_path):
    """
    Load JSON data from a file.

    Args:
    - file_path (str): Path to the JSON file.

    Returns:
    - list: List of dictionaries containing JSON data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON file: {file_path}. Error: {e}")
        return []

def save_json_file(file_path, data):
    """
    Save JSON data to a file.

    Args:
    - file_path (str): Path to the JSON file.
    - data (list): List of dictionaries containing JSON data.
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def calculate_velocity(lat1, lon1, lat2, lon2, time_diff_seconds):
    """
    Calculate velocity between two points in km/h.

    Args:
    - lat1 (str): Latitude of the first point.
    - lon1 (str): Longitude of the first point.
    - lat2 (str): Latitude of the second point.
    - lon2 (str): Longitude of the second point.
    - time_diff_seconds (float): Time difference between two points in seconds.

    Returns:
    - float: Velocity in km/h.
    """
    coords_1 = (float(lat1.replace(',', '.')), float(lon1.replace(',', '.')))
    coords_2 = (float(lat2.replace(',', '.')), float(lon2.replace(',', '.')))
    distance_km = great_circle(coords_1, coords_2).kilometers
    
    if time_diff_seconds == 0:
        return 0.0  # Return 0 velocity if time difference is zero
    
    velocity = (distance_km / time_diff_seconds) * 3600.0  # Convert to km/h
    return velocity

def add_features_to_json(sorted_file_path):
    """
    Add new features (real velocity, day of week, holiday indicator) to each record in sorted JSON file.
    
    Args:
    - sorted_file_path (str): Path to the sorted JSON file.
    """
    # Load sorted JSON data
    data = load_json_file(sorted_file_path)
    if not data:
        return
    
    # Iterate through data to add features
    for i in range(1, len(data)):
        current_record = data[i]
        previous_record = data[i - 1]
        
        current_datahora = int(current_record['datahora'])
        previous_datahora = int(previous_record['datahora'])
        
        # Calculate real velocity
        time_diff_seconds = (current_datahora - previous_datahora) / 1000.0
        velocity_real = calculate_velocity(previous_record['latitude'], previous_record['longitude'],
                                           current_record['latitude'], current_record['longitude'],
                                           time_diff_seconds)
        
        # Add real velocity to current record
        current_record['velocidadeReal'] = velocity_real
        
        # Add day of week
        current_datetime = datetime.datetime.utcfromtimestamp(current_datahora / 1000.0)
        day_of_week = current_datetime.weekday()
        current_record['diaSemana'] = day_of_week
        
        # Check if it's a holiday
        br_holidays = holidays.Brazil()
        current_date = current_datetime.date()
        is_holiday = "Sim" if current_date in br_holidays else "Não"
        current_record['feriado'] = is_holiday
    
    # Write updated data back to the same JSON file
    save_json_file(sorted_file_path, data)

def process_all_sorted_json_files(folder_path):
    """
    Process all sorted JSON files in the given folder path by adding new features.
    
    Args:
    - folder_path (str): Path to the folder containing sorted JSON files.
    """
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith("_sorted.json"):
                file_path = os.path.join(root, file_name)
                add_features_to_json(file_path)

def fix_json_file(file_path):
    """
    Fix JSON file by correcting the JSON array structure.
    
    Args:
    - file_path (str): Path to the JSON file to fix.
    """
    try:
        # Read the entire content of the file
        with open(file_path, 'r', encoding='utf-8') as json_file:
            content = json_file.read()
        
        # Clean up unnecessary new lines and spaces
        content = content.replace("}]\n[", ",")
        content = content.replace("}\n[", ",")
        content = content.replace("]\n[", ",")
        
        # Remove leading/trailing whitespaces
        content = content.strip()
        
        # Ensure the file ends with a correct JSON structure
        if content.startswith("[") and content.endswith("]"):
            fixed_content = content
        else:
            fixed_content = f"[{content}]"
        
        # Validate JSON structure before writing
        try:
            json.loads(fixed_content)
        except json.JSONDecodeError as e:
            print(f"JSON decode error in file {file_path}: {e}")
            return
        
        # Write the fixed content back to the file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(fixed_content)
        
        print(f"File {file_path} successfully fixed.")
    
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error fixing file {file_path}: {e}")

def fix_all_sorted_json_files(root_folder):
    """
    Recursively fix all JSON files with '_sorted.json' suffix in the given root folder.
    
    Args:
    - root_folder (str): Root folder containing 'dataGPS' and 'dataTest' subdirectories.
    """
    for root, _, files in os.walk(root_folder):
        for file_name in files:
            if file_name.endswith("_sorted.json"):
                file_path = os.path.join(root, file_name)
                fix_json_file(file_path)

def load_json_files(folder_path):
    """
    Load JSON files from the specified folder.

    Args:
    - folder_path (str): Path to the folder containing JSON files.

    Returns:
    - List[Dict]: List of dictionaries containing the JSON data.
    """
    data = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith("_sorted.json"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as json_file:
                        data.extend(json.load(json_file))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {file_path}: {e}")
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    return data

def find_main_route(data, eps=0.001, min_samples=5):
    """
    Find the main route using DBSCAN clustering.

    Args:
    - data (List[Dict]): List of dictionaries containing the GPS data.
    - eps (float): The maximum distance between two samples for them to be considered as in the same neighborhood.
    - min_samples (int): The number of samples in a neighborhood for a point to be considered as a core point.

    Returns:
    - List[Dict]: List of dictionaries containing the main route data.
    """
    coordinates = np.array([[float(d['latitude'].replace(',', '.')), float(d['longitude'].replace(',', '.'))] for d in data])
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coordinates)

    labels = clustering.labels_
    main_cluster = np.argmax(np.bincount(labels[labels >= 0]))

    main_route = [data[i] for i in range(len(data)) if labels[i] == main_cluster]

    return main_route

def remove_outliers(data, main_route):
    """
    Remove outliers from the data based on the main route.

    Args:
    - data (List[Dict]): List of dictionaries containing the GPS data.
    - main_route (List[Dict]): List of dictionaries containing the main route data.

    Returns:
    - List[Dict]: List of dictionaries containing the cleaned data.
    """
    main_route_set = set((d['latitude'], d['longitude']) for d in main_route)
    cleaned_data = [d for d in data if (d['latitude'], d['longitude']) in main_route_set]

    return cleaned_data

def process_all_files(root_folder):
    """
    Process all JSON files to find the main route and remove outliers.

    Args:
    - root_folder (str): Root folder containing 'dataGPS' and 'dataTest' subdirectories.
    """
    data_gps_path = os.path.join(root_folder, 'dataGPS')
    data_test_path = os.path.join(root_folder, 'dataTest')

    for path in [data_gps_path, data_test_path]:
        data = load_json_files(path)

        # Group data by 'ordem' and 'linha'
        grouped_data = defaultdict(list)
        for entry in data:
            key = (entry['ordem'], entry['linha'])
            grouped_data[key].append(entry)

        for key, group in grouped_data.items():
            main_route = find_main_route(group)
            cleaned_data = remove_outliers(group, main_route)

            # Save the cleaned data back to file
            file_name = f"{key[0]}_{key[1]}_cleaned.json"
            file_path = os.path.join(path, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(cleaned_data, json_file, ensure_ascii=False, indent=4)
                print(f"File {file_path} successfully saved.")
            except Exception as e:
                print(f"Error saving file {file_path}: {e}")
                                      
def main():
    # Define paths relative to the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_gps_path = os.path.join(current_dir, 'dataGPS')
    data_test_path = os.path.join(current_dir, 'dataTest')
    
    models_path = os.path.join(current_dir, 'models')
    
    # Define relevant bus lines
    relevant_lines = [
        '107', '177', '203', '222', '230', '232', '415', '2803', '324', '852', '557', '759', '343', '779', '905', '108',
        '483', '864', '639', '3', '309', '774', '629', '371', '397', '100', '838', '315', '624', '388', '918', '665',
        '328', '497', '878', '355', '138', '606', '457', '550', '803', '917', '638', '2336', '399', '298', '867', '553',
        '565', '422', '756', '186012003', '292', '554', '634', '232', '415', '2803', '324', '852', '557', '759', '343',
        '779', '905', '108'
    ]
    
    # Extract zip files
    # extract_zip_files(data_gps_path)
    # extract_zip_files(data_test_path)
    
    # Process data files
    # Filter JSON files in dataGPS folder
    # filter_json_files(data_gps_path, relevant_lines)
    
    # # Filter JSON files in dataTest folder
    # filter_json_files(data_test_path, relevant_lines)
    
    # # Group and sequence JSON files in dataGPS folder
    # group_sequence_json_files(data_gps_path)
    
    # # Group and sequence JSON files in dataTest folder
    # group_sequence_json_files(data_test_path)
    
    # # Fix files in dataGPS directory
    # fix_all_sorted_json_files(data_gps_path)
    
    # # Fix files in dataTest directory
    # fix_all_sorted_json_files(data_test_path)
    
    # process_all_files(current_dir)
    
    # Process all sorted JSON files in dataGPS folder
    # process_all_sorted_json_files(data_gps_path)
    
    # Process all sorted JSON files in dataTest folder
    # process_all_sorted_json_files(data_test_path)
    
if __name__ == "__main__":
    main()
