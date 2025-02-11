from flask import Flask, jsonify
from flask_cors import CORS
import random
import json
import os

app = Flask(__name__)
CORS(app)

# Função para simular a leitura dos sensores
def get_sensor_data():
    return {
        "temperatura": round(random.uniform(20, 80), 2),
        "umidade": round(random.uniform(30, 90), 2),
        "pressao": round(random.uniform(900, 1100), 2),
        "luminosidade": round(random.uniform(100, 1000), 2),
        "vento": round(random.uniform(0, 10), 2)
    }

# Carregar dados do sensores.json
def load_data():
    if os.path.exists('sensores.json'):
        with open('sensores.json', 'r') as f:
            return json.load(f)
    return {}

# Salvar dados no sensores.json
def save_data(data):
    with open('sensores.json', 'w') as f:
        json.dump(data, f)

@app.route('/sensores', methods=['GET'])
def sensores():
    sensor_data = get_sensor_data()
    data = load_data()
    data.update(sensor_data)

    # Salvar os dados no arquivo JSON
    save_data(data)

    # Verificar alertas
    alerts = []
    if sensor_data["temperatura"] > 75:
        alerts.append("Temperatura crítica!")
    if sensor_data["umidade"] < 35:
        alerts.append("Umidade baixa!")
    if sensor_data["pressao"] < 950:
        alerts.append("Pressão baixa!")

    return jsonify({
        "data": sensor_data,
        "alerts": alerts
    })

if __name__ == '__main__':
    app.run(debug=True)
