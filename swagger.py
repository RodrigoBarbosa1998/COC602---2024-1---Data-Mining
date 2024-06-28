from flask import Flask, request, jsonify
import os
import json
import requests

app = Flask(__name__)

# Caminhos dos diretórios
data_test_end_path = 'dataTestEnd'
models_path = 'models'

# Endpoint para receber os dados finais
@app.route('/rest/rpc/avalia', methods=['POST'])
def avalia():
    if request.method == 'POST':
        data = request.json
        
        # Verifica se os dados necessários estão presentes
        if 'aluno' not in data or 'datahora' not in data or 'previsoes' not in data or 'senha' not in data:
            return jsonify({'error': 'Dados incompletos no arquivo JSON'}), 400
        
        # Nome do aluno e senha
        aluno = data['aluno']
        senha = data['senha']
        
        # Gera o nome do arquivo baseado no aluno e na datahora
        filename = f'{aluno}_{data["datahora"]}.json'
        filepath = os.path.join(data_test_end_path, filename)
        
        # Salva o arquivo resposta.json no diretório dataTestEnd
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        
        # Resposta de sucesso
        return jsonify({'message': 'Dados recebidos e salvos com sucesso!'}), 200

# Função para enviar o arquivo resposta.json para o endpoint especificado
def enviar_testes_finais(filepath):
    url = ''
    
    # Carrega os dados do arquivo resposta.json
    with open(filepath, 'r') as file:
        data = json.load(file)
    
    # Envia os dados via POST usando requests
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print('Testes finais enviados com sucesso!')
    else:
        print(f'Erro ao enviar os testes finais: {response.status_code}')

if __name__ == '__main__':
    app.run(debug=True)

