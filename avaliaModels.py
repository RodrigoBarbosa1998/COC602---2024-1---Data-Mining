import os
import json
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import numpy as np

# Caminhos dos diretórios
current_dir = os.path.dirname(__file__)
models_path = os.path.join(current_dir, 'models')
data_test_path = os.path.join(current_dir, 'dataTest')
result_file_path = os.path.join(current_dir, 'resultPrevisor.txt')

# Linhas de ônibus relevantes
relevant_lines = [
    '107', '177', '203', '222', '230', '232', '415', '2803', '324', '852', '557', '759', '343', '779', '905', '108',
    '483', '864', '639', '3', '309', '774', '629', '371', '397', '100', '838', '315', '624', '388', '918', '665',
    '328', '497', '878', '355', '138', '606', '457', '550', '803', '917', '638', '2336', '399', '298', '867', '553',
    '565', '422', '756', '186012003', '292', '554', '634', '232', '415', '2803', '324', '852', '557', '759', '343',
    '779', '905', '108'
]

# Função para encontrar recursivamente todos os arquivos _sorted.json em um diretório
def find_sorted_json_files(directory):
    sorted_json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("_sorted.json"):
                sorted_json_files.append(os.path.join(root, file))
    return sorted_json_files

# Avaliação do modelo
results = {linha: {'mse': [], 'mae': [], 'r2': []} for linha in relevant_lines}

sorted_json_files = find_sorted_json_files(data_test_path)

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
    
    for linha in relevant_lines:
        # Filtrar dados apenas para a linha atual
        data_linha = df_relevant[df_relevant['linha'] == linha]
        
        if len(data_linha) > 0:
            # Verificar se a coluna 'velocidade' existe
            if 'velocidade' not in data_linha.columns:
                print(f"Coluna 'velocidade' não encontrada para a linha {linha} no arquivo {filepath}")
                continue
            
            # Separar features e target
            X_test = data_linha[['hora_do_dia']]
            y_test = data_linha['velocidade']
            
            # Carregar o modelo treinado
            model_filename = f'model_{linha}.joblib'
            model_path = os.path.join(models_path, model_filename)
            
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                
                # Prever as velocidades
                y_pred = model.predict(X_test)
                
                # Calcular as métricas de precisão
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Armazenar os resultados
                results[linha]['mse'].append(mse)
                results[linha]['mae'].append(mae)
                results[linha]['r2'].append(r2)
                
                print(f'Linha {linha}: MSE = {mse}, MAE = {mae}, R2 = {r2}')

# Calcular a média, variância e desvio padrão para cada linha
final_results = []
for linha, metrics in results.items():
    if metrics['mse']:
        mse_mean = np.mean(metrics['mse'])
        mse_variance = np.var(metrics['mse'])
        mse_std = np.std(metrics['mse'])
        
        mae_mean = np.mean(metrics['mae'])
        mae_variance = np.var(metrics['mae'])
        mae_std = np.std(metrics['mae'])
        
        r2_mean = np.mean(metrics['r2'])
        r2_variance = np.var(metrics['r2'])
        r2_std = np.std(metrics['r2'])
        
        final_results.append(
            f'Linha {linha}: MSE - Mean: {mse_mean}, Variance: {mse_variance}, Std: {mse_std}; '
            f'MAE - Mean: {mae_mean}, Variance: {mae_variance}, Std: {mae_std}; '
            f'R2 - Mean: {r2_mean}, Variance: {r2_variance}, Std: {r2_std}'
        )
        
# Escrever os resultados em um arquivo .txt
with open(result_file_path, 'w') as result_file:
    for result in final_results:
        result_file.write(result + '\n')

print(f'Resultados salvos em {result_file_path}')
