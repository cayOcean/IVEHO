from flask import Flask, jsonify
from flask_cors import CORS
import random
import mysql.connector
import requests

app = Flask(__name__)
CORS(app)

# === Configurações ===
THINGSPEAK_API_KEY = 'SUA_CHAVE_API'
THINGSPEAK_URL = 'https://api.thingspeak.com/update'
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sua_senha',
    'database': 'monitoramento'
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
    cursor.close()
    conn.close()

# === Enviar para o ThingSpeak ===
def send_to_thingspeak(data):
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'field1': data['temperatura'],
        'field2': data['umidade'],
        'field3': data['presença'],
        'field4': data['tensão eletrica']
    }
    try:
        requests.get(THINGSPEAK_URL, params=payload)
    except Exception as e:
        print("Erro ao enviar para o ThingSpeak:", e)

# === Rota principal ===
@app.route('/sensores', methods=['GET'])
def sensores():
    sensor_data = get_sensor_data()
    
    # Persistência
    save_to_db(sensor_data)

    # Enviar para o ThingSpeak a cada 15s (frontend vai chamar sempre, então backend envia a cada 3ª vez)
    sensores.counter = getattr(sensores, "counter", 0) + 1
    if sensores.counter % 3 == 0:
        send_to_thingspeak(sensor_data)

    # Verificação de alertas
    alerts = []
    if sensor_data["temperatura"] > 75:
        alerts.append("Temperatura crítica!")
    if sensor_data["umidade"] < 35:
        alerts.append("Umidade baixa!")
    if sensor_data["presença"] < 950:
        alerts.append("Não tem ninguém presente!")

    return jsonify({
        "data": sensor_data,
        "alerts": alerts
    })

if __name__ == '__main__':
    app.run(debug=True)
