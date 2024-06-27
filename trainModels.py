import os
import json
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import joblib

# Caminhos dos diretórios
current_dir = os.path.dirname(__file__)
data_gps_path = os.path.join(current_dir, 'dataGPS')
models_path = os.path.join(current_dir, 'models')

# Linhas de ônibus relevantes
relevant_lines = [
    '107', '177', '203', '222', '230', '232', '415', '2803', '324', '852', '557', '759', '343', '779', '905', '108',
    '483', '864', '639', '3', '309', '774', '629', '371', '397', '100', '838', '315', '624', '388', '918', '665',
    '328', '497', '878', '355', '138', '606', '457', '550', '803', '917', '638', '2336', '399', '298', '867', '553',
    '565', '422', '756', '186012003', '292', '554', '634', '232', '415', '2803', '324', '852', '557', '759', '343',
    '779', '905', '108'
]

# Função para calcular a velocidade média por linha e hora do dia
def calculate_average_speeds(data):
    data['velocidade'] = data['velocidade'].astype(float)
    avg_speeds = data.groupby(['linha', 'hora_do_dia']).agg({'velocidade': 'mean'}).reset_index()
    return avg_speeds

# Função para encontrar recursivamente todos os arquivos _sorted.json em um diretório
def find_sorted_json_files(directory):
    sorted_json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("_sorted.json"):
                sorted_json_files.append(os.path.join(root, file))
    return sorted_json_files

# Verificar se o diretório de modelos existe, caso contrário, criá-lo
if not os.path.exists(models_path):
    os.makedirs(models_path)

# Treinamento do modelo
sorted_json_files = find_sorted_json_files(data_gps_path)

for filepath in sorted_json_files:
    # Processar o arquivo JSON
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Converter para DataFrame pandas
    df = pd.DataFrame(data)
    
    # Verificar se a coluna 'linha' existe
    if 'linha' not in df.columns:
        print(f"Coluna 'linha' não encontrada no arquivo {filepath}")
        continue
    
    # Filtrar apenas as linhas relevantes
    df_relevant = df[df['linha'].astype(str).isin(relevant_lines)]
    
    # Verificar se df_relevant não está vazio
    if df_relevant.empty:
        print(f"Nenhuma linha relevante encontrada no arquivo {filepath}")
        continue
    
    # Certificar que 'datahora' seja numérico antes da conversão
    df_relevant['datahora'] = pd.to_numeric(df_relevant['datahora'], errors='coerce')
    df_relevant['datahora'] = pd.to_datetime(df_relevant['datahora'], unit='ms')
    df_relevant['hora_do_dia'] = df_relevant['datahora'].dt.hour
    
    # Calcular média das velocidades por linha e hora do dia
    avg_speeds = calculate_average_speeds(df_relevant)
    
    # Iterar sobre cada linha relevante e treinar um modelo
    for linha in relevant_lines:
        # Filtrar dados apenas para a linha atual
        data_linha = avg_speeds[avg_speeds['linha'] == linha]
        
        if len(data_linha) > 0:
            # Separar features e target
            X = data_linha[['hora_do_dia']]
            y = data_linha['velocidade']
            
            # Criar modelo de regressão (exemplo: regressão linear)
            model = make_pipeline(ColumnTransformer(transformers=[
                ('scaler', StandardScaler(), ['hora_do_dia'])
            ]), LinearRegression())
            
            # Treinar o modelo
            model.fit(X, y)
            
            # Salvar o modelo treinado
            model_filename = f'model_{linha}.joblib'
            model_path = os.path.join(models_path, model_filename)
            joblib.dump(model, model_path)
            print(f'Modelo para linha {linha} salvo em {model_path}')
