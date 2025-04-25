from flask import Flask, jsonify, render_template
from flask_cors import CORS
import random
import mysql.connector
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# === Configurações ===
THINGSPEAK_API_KEY = os.getenv('THINGSPEAK_API_KEY')
THINGSPEAK_CHANNEL_ID = os.getenv('THINGSPEAK_CHANNEL_ID')
THINGSPEAK_URL = 'https://api.thingspeak.com/update'

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# === Simulação dos sensores ===
def get_sensor_data():
    return {
        "temperatura": round(random.uniform(20, 80), 2),
        "umidade": round(random.uniform(30, 90), 2),
        "presença": round(random.uniform(900, 1100), 2),
        "tensão_eletrica": round(random.uniform(100, 1000), 2),
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
            data["tensão_eletrica"]
        )
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")

# === Enviar para ThingSpeak ===
def send_to_thingspeak(data):
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': data["temperatura"],
        'field2': data["umidade"],
        'field3': data["presença"],
        'field4': data["tensão_eletrica"]
    }
    try:
        response = requests.post(THINGSPEAK_URL, data=payload)
        print(f"Enviado para ThingSpeak: {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar para ThingSpeak: {e}")

# === Tarefa agendada ===
def coletar_dados():
    dados = get_sensor_data()
    print("Dados coletados:", dados)
    save_to_db(dados)
    send_to_thingspeak(dados)

scheduler = BackgroundScheduler()
scheduler.add_job(coletar_dados, 'interval', seconds=30)
scheduler.start()

@app.route('/sensores')
def get_sensores():
    try:
        dados = get_sensor_data()
        return jsonify({
            "alerts": [],
            "data": dados
        })
    except Exception as e:
        return jsonify({
            "alerts": [f"Erro interno no servidor: {str(e)}"],
            "data": {}
        }), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
