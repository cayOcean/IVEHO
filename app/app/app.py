from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import random
import mysql.connector
import requests

app = Flask(__name__)
CORS(app)

# === Configurações ===
THINGSPEAK_API_KEY = 'MLGZ3GKY4QDDNF8J'
THINGSPEAK_URL = 'https://api.thingspeak.com/update'
DB_CONFIG = {
    'host': 'db',  # nome do serviço no docker-compose
    'user': 'root',
    'password': '123456',
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
def send_to_thingspeak(temperatura, umidade, presenca, tensao_eletrica):
    url = f'https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}&field1={temperatura}&field2={umidade}&field3={presenca}&field4={tensao_eletrica}'
    resposta = requests.get(url)
    print(f"Resposta do ThingSpeak: {resposta.text}")

@app.route('/')
def home():
    return render_template('index.html')

# === Rota para retornar os dados dos sensores ===
@app.route('/sensores')
def sensores():
    dados = get_sensor_data()
    # Aqui você pode adicionar lógicas de alerta, se necessário
    alerts = []
    
    # Verificando se algum valor está fora do esperado e adicionando alerta
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

# === Rota para simular e registrar dados ===
@app.route('/registrar', methods=['POST'])
def registrar():
    dados = get_sensor_data()
    save_to_db(dados)
    send_to_thingspeak(
        dados["temperatura"],
        dados["umidade"],
        dados["presença"],
        dados["tensão eletrica"]
    )
    return jsonify({"mensagem": "Dados registrados com sucesso!", "dados": dados})

# === Rodar o servidor Flask ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
