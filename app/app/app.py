from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import random
import mysql.connector
import requests
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# === Configurações ===
THINGSPEAK_API_KEY = os.getenv('MLGZ3GKY4QDDNF8J')  # Leitura da variável de ambiente
THINGSPEAK_URL = 'https://api.thingspeak.com/update'
DB_CONFIG = {
    'host': 'db',  # Nome do serviço no docker-compose
    'user': 'root',
    'password': 'password',
    'database': 'monitoramento_db'
}

# === Simulação dos sensores ===
def get_sensor_data():
    return {
        "temperatura": round(random.uniform(20, 80), 2),
        "umidade": round(random.uniform(30, 90), 2),
        "presença": round(random.uniform(900, 1100), 2),
        "tensão eletrica": round(random.uniform(100, 1000), 2),
    }

# === Salvar no MySQL ===
def save_to_db(data):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = """
            INSERT INTO sensores (temperatura, umidade, presenca, tensao_eletrica)
            VALUES (%s, %s, %s, %s)
        """
        valores = (
            data["temperatura"],
            data["umidade"],
            data["presença"],
            data["tensão eletrica"]
        )
        cursor.execute(sql, valores)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        cursor.close()
        conn.close()

# === Enviar para o ThingSpeak ===
def send_to_thingspeak(temperatura, umidade, presenca, tensao_eletrica):
    try:
        url = f'https://api.thingspeak.com/update?api_key={MLGZ3GKY4QDDNF8J}&field1={temperatura}&field2={umidade}&field3={presenca}&field4={tensao_eletrica}'
        resposta = requests.get(url)
        print(f"Resposta do ThingSpeak: {resposta.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar dados para o ThingSpeak: {e}")

@app.route('/')
def home():
    return render_template('index.html')

# === Rota para retornar os dados dos sensores ===
@app.route('/sensores')
def sensores():
    dados = get_sensor_data()
    # Lógica de alerta (caso necessário)
    alerts = []
    
    if dados["temperatura"] > 70:
        alerts.append("Temperatura acima do limite!")
    if dados["umidade"] < 40:
        alerts.append("Umidade abaixo do limite!")
    if dados["presença"] > 1050:
        alerts.append("Presença detectada fora do limite!")
    if dados["tensão eletrica"] < 200:
        alerts.append("Tensão elétrica abaixo do limite!")

    return jsonify({
        "data": dados,
        "alerts": alerts
    })

@app.route('/dados')
def dados():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensores ORDER BY data_registro DESC LIMIT 5")
        dados = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erro ao acessar dados do banco: {err}")
        return jsonify({"error": "Erro ao acessar dados do banco de dados"}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(dados)

@app.route('/registrar', methods=['POST'])
def registrar():
    dados = get_sensor_data()  # Gera dados aleatórios dos sensores
    save_to_db(dados)  # Salva os dados no banco
    send_to_thingspeak(
        dados["temperatura"],
        dados["umidade"],
        dados["presença"],
        dados["tensão eletrica"]
    )
    return jsonify({"mensagem": "Dados registrados com sucesso!", "dados": dados})

# Função para inserir dados periodicamente
def inserir_dados_periodicamente():
    dados = get_sensor_data()  # Gera dados aleatórios dos sensores
    save_to_db(dados)  # Salva no banco
    print(f"Dados inseridos: {dados}")

# Configuração do agendador para inserir dados a cada 30 segundos
scheduler = BackgroundScheduler()
scheduler.add_job(inserir_dados_periodicamente, 'interval', seconds=30)
scheduler.start()

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except (KeyboardInterrupt, SystemExit):
        pass
