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
        presSpan.textContent = data.presença;
        lumSpan.textContent = data["tensão eletrica"];

        alertsDiv.innerHTML = alerts.length > 0
            ? `<p style="color:red;">${alerts.join("<br>")}</p>`
            : `<p style="color:green;">Todos os sensores estão dentro dos limites.</p>`;

        // Atualizar o gráfico
        sensorChart.data.labels.push(now);
        sensorChart.data.datasets[0].data.push(data.temperatura);
        sensorChart.data.datasets[1].data.push(data.umidade);
        sensorChart.data.datasets[2].data.push(data.presença);
        sensorChart.data.datasets[3].data.push(data["tensão eletrica"]);

        // Limitar a quantidade de pontos no gráfico (opcional)
        if (sensorChart.data.labels.length > 10) {
            sensorChart.data.labels.shift();
            sensorChart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        sensorChart.update();
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
        fetchSensorData(); // disparar já o primeiro
        intervalId = setInterval(fetchSensorData, 5000); // a cada 5 segundos
        toggleButton.textContent = "Parar Leitura";
    }
});
