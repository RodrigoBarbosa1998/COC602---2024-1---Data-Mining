import os
import json
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

# Caminhos dos diretórios
data_test_path = './dataTestEnd'
models_path = './models'

# Função para carregar modelos treinados
def load_models():
    models = {}
    for filename in os.listdir(models_path):
        if filename.endswith('.joblib'):
            model = joblib.load(os.path.join(models_path, filename))
            if filename.startswith('model_speed'):
                linha = filename.split('_')[2].split('.')[0]
                models[(linha, 'speed')] = model
            elif filename.startswith('model_coords'):
                linha = filename.split('_')[2].split('.')[0]
                models[(linha, 'coords')] = model
    return models

# Função para prever latitude e longitude dado um timestamp e uma velocidade
def predict_coordinates(model, timestamp, velocidade, last_known_coords):
    try:
        # Converter timestamp para hora do dia
        datahora = datetime.fromtimestamp(int(timestamp) / 1000)
        hora_do_dia = datahora.hour
        
        # Preparar os dados para previsão
        X_pred = pd.DataFrame({'hora_do_dia': [hora_do_dia], 'velocidade': [velocidade]})
        
        predicted = model.predict(X_pred)
        if len(predicted[0]) == 2:
            return predicted[0].tolist()  # Retorna a previsão como uma lista
    except Exception as e:
        print(f"Erro ao prever coordenadas: {e}")
    
    # Fallback: Retornar a última coordenada conhecida com um pequeno ajuste
    return [last_known_coords[0] + 0.0001, last_known_coords[1] + 0.0001]

# Função para prever timestamp dado latitude, longitude e uma velocidade
def predict_timestamp(model, latitude, longitude, velocidade, last_known_timestamp):
    try:
        # Converter last_known_timestamp para hora do dia
        datahora = datetime.fromtimestamp(int(last_known_timestamp) / 1000)
        hora_do_dia = datahora.hour
        
        # Preparar os dados para previsão
        X_pred = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude], 'velocidade': [velocidade], 'hora_do_dia': [hora_do_dia]})
        
        predicted = model.predict(X_pred)
        if len(predicted) > 0:
            return predicted[0]  # Retorna o primeiro elemento da previsão
    except Exception as e:
        print(f"Erro ao prever timestamp: {e}")
    
    # Fallback: Retornar o último timestamp conhecido com um pequeno incremento
    return last_known_timestamp + 60000  # Incrementa 1 minuto (60000 ms)

# Função para processar arquivos de teste e gerar previsões
def process_test_files(models):
    results = []
    last_known_coords = [0.0, 0.0]
    last_known_timestamp = 1715930000000  # Um timestamp inicial padrão
    
    # Iterar sobre arquivos de teste
    for root, _, files in os.walk(data_test_path):
        for file in files:
            if file.startswith('teste-') and file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                # Ler arquivo JSON de teste
                with open(filepath, 'r') as f:
                    test_data = json.load(f)
                
                for data in test_data:
                    if 'id' in data:
                        id = data['id']
                    elif 'ordem' in data:
                        id = data['ordem']
                    else:
                        print(f"Chave 'id' ou 'ordem' não encontrada no arquivo {file}.")
                        continue
                    
                    linha = data['linha']
                    
                    # Usar velocidade padrão se não estiver presente
                    velocidade = data.get('velocidade', 30)  # Usando 30 como velocidade padrão
                    
                    if 'datahora' in data:
                        # Temos timestamp, prever latitude e longitude
                        timestamp = data['datahora']
                        if (linha, 'coords') in models:
                            model_coords = models[(linha, 'coords')]
                            predicted_coords = predict_coordinates(model_coords, timestamp, velocidade, last_known_coords)
                            if len(predicted_coords) == 2:
                                results.append([id, predicted_coords[0], predicted_coords[1]])
                                last_known_coords = predicted_coords
                            else:
                                print(f"Previsão inválida para ID {id} no arquivo {file}.")
                        else:
                            print(f"Modelo de coordenadas para linha {linha} não encontrado.")
                    
                    elif 'latitude' in data and 'longitude' in data:
                        # Temos latitude e longitude, prever timestamp
                        latitude = float(data['latitude'].replace(',', '.'))
                        longitude = float(data['longitude'].replace(',', '.'))
                        if (linha, 'speed') in models:
                            model_speed = models[(linha, 'speed')]
                            timestamp = predict_timestamp(model_speed, latitude, longitude, velocidade, last_known_timestamp)
                            results.append([id, timestamp])
                            last_known_timestamp = timestamp
                        else:
                            print(f"Modelo de velocidade para linha {linha} não encontrado.")
                    
                    else:
                        print(f"Dados incompletos para previsão no arquivo {file}: {data}")
    
    return results

# Função para salvar resultados no formato resposta.json
def save_results(results):
    aluno = "Rodrigo de Oliveira Barbosa"
    datahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    senha = "myResult2024-1"
    
    previsoes = []
    for result in results:
        if len(result) == 3:
            previsoes.append({"id": result[0], "latitude": result[1], "longitude": result[2]})
        elif len(result) == 2:
            previsoes.append({"id": result[0], "datahora": result[1]})
    
    response_data = {
        "aluno": aluno,
        "datahora": datahora,
        "previsoes": previsoes,
        "senha": senha
    }
    
    with open('resposta.json', 'w') as f:
        json.dump(response_data, f, indent=4)

# Carregar modelos treinados
models = load_models()

# Processar arquivos de teste e gerar previsões
results = process_test_files(models)

# Salvar resultados no arquivo resposta.json
save_results(results)

print("Previsões concluídas e resultados salvos em resposta.json.")
