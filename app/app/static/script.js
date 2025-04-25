const tempSpan = document.getElementById("temp");
const humSpan = document.getElementById("hum");
const presSpan = document.getElementById("pres");
const lumSpan = document.getElementById("lum");
const alertsDiv = document.getElementById("alerts");
const toggleButton = document.getElementById("toggleButton");

let intervalId = null;

// Gráfico Chart.js
const ctx = document.getElementById('sensorChart').getContext('2d');
const sensorChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Horários
        datasets: [
            {
                label: 'Temperatura (ºC)',
                data: [],
                borderColor: 'red',
                fill: false
            },
            {
                label: 'Umidade (%)',
                data: [],
                borderColor: 'blue',
                fill: false
            },
            {
                label: 'Presença',
                data: [],
                borderColor: 'green',
                fill: false
            },
            {
                label: 'Tensão Elétrica (V)',
                data: [],
                borderColor: 'orange',
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Horário'
                }
            },
            y: {
                beginAtZero: true
            }
        }
    }
});

// Função para enviar dados para o ThingSpeak
async function sendDataToThingSpeak(temperatura, umidade, presenca, tensao) {
    const apiKey = 'MLGZ3GKY4QDDNF8J'; // Substitua pela sua chave de escrita
    const url = `https://api.thingspeak.com/update?api_key=${apiKey}&field1=${temperatura}&field2=${umidade}&field3=${presenca}&field4=${tensao}`;

    try {
        const response = await fetch(url);
        if (response.ok) {
            console.log('Dados enviados com sucesso para o ThingSpeak');
        } else {
            console.error('Erro ao enviar dados para o ThingSpeak');
        }
    } catch (error) {
        console.error('Erro na requisição para o ThingSpeak:', error);
    }
}

// Função para buscar os dados
async function fetchSensorData() {
    try {
        const response = await fetch('http://localhost:5000/sensores'); // Alterado para a URL correta
        const json = await response.json();
        const data = json.data;
        const alerts = json.alerts;

        const now = new Date().toLocaleTimeString();

        tempSpan.textContent = data.temperatura;
        humSpan.textContent = data.umidade;
        presSpan.textContent = data.presenca;
        lumSpan.textContent = data["tensao_eletrica"]; // Ajustado para 'tensao_eletrica'

        // Mostrar alertas
        alertsDiv.innerHTML = alerts.length > 0
            ? `<p style="color:red;">${alerts.join("<br>")}</p>`
            : `<p style="color:green;">Todos os sensores estão dentro dos limites.</p>`;

        // Atualizar o gráfico
        sensorChart.data.labels.push(now);
        sensorChart.data.datasets[0].data.push(data.temperatura);
        sensorChart.data.datasets[1].data.push(data.umidade);
        sensorChart.data.datasets[2].data.push(data.presenca);
        sensorChart.data.datasets[3].data.push(data["tensao_eletrica"]);

        // Limitar a quantidade de pontos no gráfico (opcional)
        if (sensorChart.data.labels.length > 10) {
            sensorChart.data.labels.shift();
            sensorChart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        sensorChart.update();

        // Enviar dados para o ThingSpeak
        sendDataToThingSpeak(data.temperatura, data.umidade, data.presenca, data["tensao_eletrica"]);

    } catch (error) {
        console.error("Erro ao buscar dados:", error);
        alertsDiv.innerHTML = `<p style="color:darkred;">Erro ao buscar dados do servidor.</p>`;
    }
}

// Botão de iniciar/parar leitura
toggleButton.addEventListener("click", () => {
    if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
        toggleButton.textContent = "Iniciar Leitura";
    } else {
        fetchSensorData(); // Disparar já o primeiro
        intervalId = setInterval(fetchSensorData, 5000); // a cada 5 segundos
        toggleButton.textContent = "Parar Leitura";
    }
});
