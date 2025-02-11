const ctx = document.getElementById('sensorChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'Temperatura (ºC)', data: [], borderColor: 'red', fill: false },
            { label: 'Umidade (%)', data: [], borderColor: 'blue', fill: false },
            { label: 'Pressão (hPa)', data: [], borderColor: 'green', fill: false },
            { label: 'Luminosidade (lux)', data: [], borderColor: 'yellow', fill: false },
            { label: 'Vento (m/s)', data: [], borderColor: 'purple', fill: false }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: { title: { display: true, text: 'Tempo' } }
        }
    }
});

let intervalo;
let leituraAtiva = false;

document.getElementById('toggleButton').addEventListener('click', function() {
    if (leituraAtiva) {
        clearInterval(intervalo);
        document.getElementById('toggleButton').innerText = 'Iniciar Leitura';
    } else {
        intervalo = setInterval(atualizarSensores, 2000);
        document.getElementById('toggleButton').innerText = 'Pausar Leitura';
    }
    leituraAtiva = !leituraAtiva;
});

async function atualizarSensores() {
    try {
        const response = await fetch('http://127.0.0.1:5000/sensores');
        const data = await response.json();

        // Atualiza os valores no HTML
        document.getElementById('temp').innerText = data.data.temperatura;
        document.getElementById('hum').innerText = data.data.umidade;
        document.getElementById('pres').innerText = data.data.pressao;
        document.getElementById('lum').innerText = data.data.luminosidade;
        document.getElementById('vento').innerText = data.data.vento;

        // Exibe os alertas, se houver
        document.getElementById('alerts').innerHTML = data.alerts.map(alert => `<p>${alert}</p>`).join('');

        // Atualiza o gráfico
        const now = new Date().toLocaleTimeString();
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.data.temperatura);
        chart.data.datasets[1].data.push(data.data.umidade);
        chart.data.datasets[2].data.push(data.data.pressao);
        chart.data.datasets[3].data.push(data.data.luminosidade);
        chart.data.datasets[4].data.push(data.data.vento);

        if (chart.data.labels.length > 10) {
            chart.data.labels.shift();
            chart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        chart.update();
    } catch (error) {
        console.error("Erro ao buscar dados:", error);
    }
}
