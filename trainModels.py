import os
import json
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json

def load_processed_data(folder_path):
    """
    Load all processed JSON files in the given folder into a DataFrame.
    """
    data_frames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.startswith("processed_") and file.endswith(".json"):
                file_path = os.path.join(root, file)
                print(f"Loading file: {file_path}")
                try:
                    df = pd.read_json(file_path, lines=True)
                    data_frames.append(df)
                except ValueError as e:
                    print(f"Error loading {file_path}: {e}")
    if not data_frames:
        print("No data frames loaded.")
        return pd.DataFrame()
    return pd.concat(data_frames, ignore_index=True)

def train_and_save_models(df, lines):
    """
    Train and save Prophet models for each bus line.
    """
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    for line in lines:
        df_line = df[df['linha'] == line]
        if df_line.empty:
            print(f"No data for line {line}.")
            continue
        df_prophet = df_line[['datahora', 'ordem']]
        df_prophet.columns = ['ds', 'y']
        
        model = Prophet()
        model.fit(df_prophet)
        
        model_path = os.path.join(models_dir, f"model_{line}.json")
        with open(model_path, 'w') as f:
            f.write(model_to_json(model))
        
        print(f"Trained and saved the Prophet model for line {line} to {model_path}")

def main():
    # Define paths relative to the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    processed_data_path = os.path.join(current_dir, 'dataGPS', 'processed')
    
    # Check if the directory exists
    if not os.path.exists(processed_data_path):
        print(f"Processed data directory does not exist: {processed_data_path}")
        return
    
    # Define relevant bus lines
    relevant_lines = [
        '107', '177', '203', '222', '230', '232', '415', '2803', '324', '852', '557', '759', '343', '779', '905', '108',
        '483', '864', '639', '3', '309', '774', '629', '371', '397', '100', '838', '315', '624', '388', '918', '665',
        '328', '497', '878', '355', '138', '606', '457', '550', '803', '917', '638', '2336', '399', '298', '867', '553',
        '565', '422', '756', '186012003', '292', '554', '634', '232', '415', '2803', '324', '852', '557', '759', '343',
        '779', '905', '108'
    ]
    
    # Load processed data
    combined_df = load_processed_data(processed_data_path)
    
    if combined_df.empty:
        print("No processed data available.")
        return
    
    # Train and save models
    train_and_save_models(combined_df, relevant_lines)

if __name__ == "__main__":
    main()
