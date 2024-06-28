# Previsão de Localização de Ônibus - Processamento de Dados GPS

ste trabalho será sobre a previsão da localização de ônibus dado um histórico de posições de GPS. Este projeto visa o processamento de dados JSON relacionados aos registros de GPS de ônibus e dados de teste. O objetivo é extrair, filtrar, sequenciar, adicionar funcionalidades e limpar os dados para análises posteriores.

Os dados são muito sujos e de baixa qualidade em determinados horários, principalmente noite/madrugada. Além disso, nem sempre o motorista desliga o GPS ao ir para a garagem ou altera a vista da linha do ônibus. Iremos realizar previsões apenas durante os trajetos normais dos ônibus, e no horário entre 08:00 e 23:00.


## 1) Extração de Arquivos ZIP

### Função: `extract_zip_files`

#### Objetivo:
Extrai todos os arquivos ZIP encontrados em um diretório especificado.

#### Entrada:
- `folder_path` (str): Caminho para a pasta contendo arquivos ZIP.

#### Processo:
- Itera sobre todos os arquivos no diretório especificado.
- Verifica se cada arquivo termina com ".zip".
- Extrai o conteúdo de cada arquivo ZIP para o mesmo diretório.

#### Exemplo de Uso:
- `extract_zip_files(data_gps_path)`
- `extract_zip_files(data_test_path)`

## 2) Filtragem de Arquivos JSON

### Função: `filter_json_files`

#### Objetivo:
Filtrar arquivos JSON recursivamente em um diretório e subdiretórios, mantendo apenas registros de linhas de ônibus relevantes.

#### Entrada:
- `folder_path` (str): Caminho para a pasta contendo arquivos JSON.
- `relevant_lines` (list): Lista de linhas de ônibus relevantes para filtragem.

#### Processo:
- Percorre todos os arquivos JSON no diretório e subdiretórios.
- Carrega cada arquivo JSON, filtra registros com base nas linhas de ônibus relevantes e reescreve o arquivo com os registros filtrados.

#### Exemplo de Uso:
- `filter_json_files(data_gps_path, relevant_lines)`
- `filter_json_files(data_test_path, relevant_lines)`

## 3) Agrupamento e Sequenciamento de Arquivos JSON

### Função: `group_sequence_json_files`

#### Objetivo:
Agrupa arquivos JSON por 'linha' e sequencia por 'datahora', reescrevendo os arquivos JSON.

#### Entrada:
- `folder_path` (str): Caminho para a pasta contendo arquivos JSON.

#### Processo:
- Lê cada arquivo JSON no diretório.
- Agrupa registros por 'linha'.
- Ordena registros por 'datahora' dentro de cada 'linha'.
- Escreve os registros ordenados de volta para novos arquivos JSON.

#### Exemplo de Uso:
- `group_sequence_json_files(data_gps_path)`
- `group_sequence_json_files(data_test_path)`

## 4) Correção de Arquivos JSON

### Função: `fix_json_file`

#### Objetivo:
Corrige a estrutura de arquivos JSON corrigindo erros de formatação.

#### Entrada:
- `file_path` (str): Caminho para o arquivo JSON a ser corrigido.

#### Processo:
- Lê o conteúdo completo do arquivo JSON.
- Limpa novas linhas e espaços desnecessários.
- Garante que o arquivo termine com uma estrutura JSON válida.

#### Exemplo de Uso:
- `fix_json_file(file_path)`

## 5) Adição de Novas Funcionalidades aos Arquivos JSON

### Função: `add_features_to_json`

#### Objetivo:
Adiciona novas funcionalidades (velocidade real, dia da semana, indicador de feriado) a cada registro no arquivo JSON ordenado.

#### Entrada:
- `sorted_file_path` (str): Caminho para o arquivo JSON ordenado.

#### Processo:
- Carrega os dados JSON ordenados.
- Calcula a velocidade real entre registros consecutivos.
- Adiciona a velocidade real, dia da semana e indicador de feriado a cada registro.
- Escreve os dados atualizados de volta ao arquivo JSON.

#### Exemplo de Uso:
- `add_features_to_json(sorted_file_path)`

## 6) Processamento de Todos os Arquivos JSON Ordenados

### Função: `process_all_sorted_json_files`

#### Objetivo:
Processa todos os arquivos JSON ordenados em um diretório, adicionando novas funcionalidades.

#### Entrada:
- `folder_path` (str): Caminho para a pasta contendo arquivos JSON ordenados.

#### Processo:
- Itera sobre todos os arquivos no diretório especificado.
- Chama a função `add_features_to_json` para cada arquivo JSON ordenado.

#### Exemplo de Uso:
- `process_all_sorted_json_files(data_gps_path)`
- `process_all_sorted_json_files(data_test_path)`

## 7) Processamento Completo de Arquivos

### Função: `process_all_files`

#### Objetivo:
Processa todos os arquivos JSON para encontrar a rota principal e remover outliers.

#### Entrada:
- `root_folder` (str): Pasta raiz contendo subdiretórios 'dataGPS' e 'dataTest'.

#### Processo:
- Carrega e processa arquivos JSON em 'dataGPS' e 'dataTest'.
- Agrupa dados por 'ordem' e 'linha'.
- Encontra a rota principal usando DBSCAN para agrupamento.
- Criação de uma cerca virtual em torno dos pontos médios, gerando o caminho principal.
- Remove outliers com base na rota principal encontrada.
- Salva os dados limpos de volta aos arquivos.

#### Exemplo de Uso:
- `process_all_files(current_dir)`

## Função Principal: `main`

A função `main` coordena todas as etapas do processamento de dados:

- Define os caminhos para os diretórios 'dataGPS' e 'dataTest'.
- Define as linhas de ônibus relevantes.
- Extrai arquivos ZIP.
- Filtra e agrupa arquivos JSON.
- Corrige arquivos JSON.
- Adiciona novas funcionalidades aos arquivos JSON ordenados.
- Processa todos os arquivos JSON ordenados.
- Processa todos os arquivos para encontrar a rota principal e remover outliers.

### Exemplo de Uso:
- Executa `main()` para iniciar o processamento completo dos dados.


# Predição de Localização dos Ônibus - Treinamento de Modelos

Após o processamento inicial dos dados de GPS dos ônibus, o próximo passo no projeto é o treinamento de modelos para prever a localização dos ônibus com base nos registros históricos de GPS. Esta etapa visa utilizar os dados limpos e enriquecidos para criar modelos que possam estimar a velocidade média do ônibus, bem como prever suas coordenadas de latitude e longitude em intervalos futuros.

## 1) Preparação dos Dados

Após o processamento dos arquivos JSON, que incluiu extração, filtragem, correção de erros e adição de novas funcionalidades, os dados estão prontos para serem utilizados no treinamento dos modelos. Os arquivos foram agrupados por linha de ônibus e horário do dia, permitindo uma visão mais clara das tendências de movimento e comportamento dos ônibus ao longo do tempo.

## 2) Treinamento dos Modelos

Para cada linha de ônibus relevante, foram treinados dois tipos de modelos:

### Modelo de Velocidade Média:

Este modelo utiliza como características a hora do dia, latitude e longitude médias.
O objetivo é prever a velocidade média do ônibus em diferentes momentos do dia, levando em conta variações de tráfego.

### Modelo de Coordenadas (Latitude e Longitude):

Este modelo utiliza como características a hora do dia e a velocidade média.
O objetivo é prever as coordenadas de latitude e longitude do ônibus em intervalos futuros, com base na velocidade média esperada e no horário do dia.

## 3) Implementação dos Modelos

Os modelos foram implementados usando a biblioteca Scikit-Learn em Python, aproveitando os recursos de pipelines para escala e transformação de características, além de utilizar regressão linear para a previsão. Após o treinamento, os modelos foram salvos em arquivos .joblib para uso posterior na fase de previsão.

Com os modelos treinados e salvos, o próximo passo será a fase de avaliação e validação. Serão utilizados conjuntos de dados de teste para verificar a precisão das previsões de localização dos ônibus. 


# Avaliação do Modelo

Aavaliação de modelos para diferentes linhas de ônibus, usando métricas como Mean Squared Error (MSE), Mean Absolute Error (MAE) e Coefficient of Determination (R2). 

## 1) Importações e Configurações Iniciais:
- O código importa os módulos necessários, incluindo operações de sistema (os), manipulação de JSON (json), manipulação de dados (pandas), métricas de regressão (sklearn.metrics), persistência de modelos (joblib) e manipulação numérica (numpy).
- Define caminhos para diretórios de modelos, dados de teste e arquivo de resultados.

## 2) Linhas de Ônibus Relevantes

- São listadas as linhas de ônibus específicas para as quais os modelos serão avaliados.

## 3) Função find_sorted_json_files:

- Esta função recursivamente busca por arquivos _sorted.json no diretório especificado (data_test_path).

## 4) Avaliação do Modelo:

- Um dicionário results é inicializado para armazenar as métricas de cada linha de ônibus relevante.
- Itera-se sobre os arquivos JSON encontrados (sorted_json_files), carregando os dados, convertendo-os em um DataFrame do Pandas e filtrando apenas os dados relevantes para cada linha de ônibus.

## 5) Loop Interno por Linha de Ônibus:

- Para cada linha de ônibus, são carregados os modelos treinados previamente (model_filename), predizendo as velocidades (y_pred) com base nos dados de teste (X_test).
- São calculadas as métricas MSE, MAE e R2 entre as velocidades reais (y_test) e as preditas (y_pred).
- As métricas são armazenadas no dicionário results para cada linha de ônibus.

## 6) Escrita dos Resultados em Arquivo:

- Os resultados finais são escritos no arquivo resultPrevisor.txt, exibindo as estatísticas calculadas para cada linha de ônibus.


# Previsão

## 1) Função load_models:

- Esta função carrega os modelos treinados a partir dos arquivos .joblib no diretório especificado (models_path). Ela itera sobre os arquivos, identifica o tipo de modelo pelo nome do arquivo (model_speed para velocidade e model_coords para coordenadas) e os armazena em um dicionário models, usando uma tupla (linha, tipo) como chave.

## 2) Função predict_coordinates:

- Utiliza um modelo treinado para prever latitude e longitude com base em um timestamp e uma velocidade fornecidos. Primeiro, converte o timestamp para hora do dia, prepara os dados para previsão (X_pred), e então realiza a previsão usando o modelo. Se a previsão for bem-sucedida, retorna as coordenadas previstas como uma lista. 

## 3) Função predict_timestamp:

- Esta função prevê um timestamp com base em latitude, longitude e velocidade fornecidos, utilizando um modelo treinado. Converte o último timestamp conhecido para hora do dia, prepara os dados (X_pred), e realiza a previsão. Retorna o primeiro elemento da previsão se bem-sucedido.

## 4) Função process_test_files:

- Esta função processa os arquivos de teste localizados em data_test_path. Itera sobre cada arquivo JSON, lendo os dados e processando-os para previsões. Dependendo dos dados disponíveis (datahora para prever coordenadas ou latitude/longitude para prever timestamp), utiliza os modelos adequados carregados anteriormente para gerar as previsões. Armazena os resultados em uma lista results.

## 5) Função save_results:

- Esta função formata os resultados das previsões em um formato específico e os salva em um arquivo JSON chamado resposta.json. Inclui informações como o nome do aluno, a data e hora da geração do arquivo, as previsões feitas e uma senha.
- Este código é estruturado para carregar modelos treinados, realizar previsões com base nos dados de teste fornecidos e salvar os resultados em um formato específico para análise posterior.