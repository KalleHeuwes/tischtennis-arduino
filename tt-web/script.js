let sensorLog = [];
let minX = Infinity, maxX = -Infinity;
let minY = Infinity, maxY = -Infinity;
let minZ = Infinity, maxZ = -Infinity;
let minXg= Infinity, maxXg= -Infinity;
let minYg= Infinity, maxYg= -Infinity;
let minZg= Infinity, maxZg= -Infinity;
let minXm= Infinity, maxXm= -Infinity;
let minYm= Infinity, maxYm= -Infinity;
let minZm= Infinity, maxZm= -Infinity;
let logMe = 1;

const maxPointsInGraph = 60;
let scale1 = 8;
let scale2 = 500;
const ctx = document.getElementById('liveChart').getContext('2d');
const enableChartCheckbox = document.getElementById('enableChart');
const liveChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            // Datensätze für die linke Achse (-scale1 bis scale1)
            { label: 'X (Beschleunigung)', borderColor: '#ff5252', data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y' },
            { label: 'Y (Beschleunigung)', borderColor: '#4caf50', data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y' },
            { label: 'Z (Beschleunigung)', borderColor: '#2196f3', data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y' },
            
            // Datensätze für die rechte Achse (-scale2 bis scale2)
            { label: 'X (Drehung)', borderColor: '#ff5252', borderDash: [5, 5], data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y1' },
            { label: 'Y (Drehung)', borderColor: '#4caf50', borderDash: [5, 5], data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y1' },
            { label: 'Z (Drehung)', borderColor: '#2196f3', borderDash: [5, 5], data: [], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y1' }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
            x: { display: false },
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                min: -1 * scale1,
                max: scale1,
                title: { display: true, text: 'Skala Beschleunigung' }
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                min: -1 * scale2,
                max: scale2,
                title: { display: true, text: 'Skala Drehung' },
                // Wichtig: Rasterlinien der zweiten Achse meist ausblenden, damit das Chart nicht "überladen" wirkt
                grid: { drawOnChartArea: false }
            }
        }
    }
});

const ctx3 = document.getElementById('liveChart3').getContext('2d');
const liveChart3 = new Chart(ctx3, {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{ label: 'X (Magneto)', borderColor: '#ff5252', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Y (Magneto)', borderColor: '#4caf50', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Z (Magneto)', borderColor: '#2196f3', data: [], borderWidth: 2, pointRadius: 0, fill: false }
		]
	},
	options: {
		responsive: true,
		maintainAspectRatio: false,
		animation: false,
		scales: {
			y: { min: -100, max: 100 },
			x: { display: false }
		}
	}
});

const SERVICE_UUID = 0x1101;
const CHARACTERISTIC_UUID = 0x2101;
const needleWrapper = document.getElementById('needleWrapper');
const headingValueSpan = document.getElementById('headingValue');

document.getElementById('connectBtn').addEventListener('click', async () => {
	try {
		const device = await navigator.bluetooth.requestDevice({
			filters: [{ name: 'Nano33_IMU' }],
			optionalServices: [SERVICE_UUID]
		});

		const server = await device.gatt.connect();
		const service = await server.getPrimaryService(SERVICE_UUID);
		const char = await service.getCharacteristic(CHARACTERISTIC_UUID);

		await char.startNotifications();
		document.getElementById('statusText').innerText = "Verbunden";
		//document.getElementById('connectBtn').disabled = true;
		document.getElementById('downloadBtn').disabled = false;

		char.addEventListener('characteristicvaluechanged', (event) => {
			const rawString = new TextDecoder().decode(event.target.value);
			const [ax, ay, az, gx, gy, gz, mx, my, mz] = rawString.split(',').map(Number);
			
			const now = new Date();
			const timeStr = now.toLocaleTimeString() + "." + now.getMilliseconds().toString().padStart(3, '0');

			// Extremwerte berechnen
			if (ax < minX)  minX  = ax; if (ax > maxX)  maxX = ax;
			if (ay < minY)  minY  = ay; if (ay > maxY)  maxY = ay;
			if (az < minZ)  minZ  = az; if (az > maxZ)  maxZ = az;
			if (gx < minXg) minXg = gx; if (gx > maxXg) maxXg= gx;
			if (gy < minYg) minYg = gy; if (gy > maxYg) maxYg= gy;
			if (gz < minZg) minZg = gz; if (gz > maxZg) maxZg= gz;
			if (mx < minXm) minXm = mx; if (mx > maxXm) maxXm= mx;
			if (my < minYm) minYm = my; if (my > maxYm) maxYm= my;
			if (mz < minZm) minZm = mz; if (mz > maxZm) maxZm= mz;

			// UI Tabelle aktualisieren
			document.getElementById('nowX').innerText = ax.toFixed(2);
			document.getElementById('minX').innerText = minX.toFixed(2);
			document.getElementById('maxX').innerText = maxX.toFixed(2);

			document.getElementById('nowY').innerText = ay.toFixed(2);
			document.getElementById('minY').innerText = minY.toFixed(2);
			document.getElementById('maxY').innerText = maxY.toFixed(2);

			document.getElementById('nowZ').innerText = az.toFixed(2);
			document.getElementById('minZ').innerText = minZ.toFixed(2);
			document.getElementById('maxZ').innerText = maxZ.toFixed(2);

			// UI Tabelle aktualisieren Gyro
			document.getElementById('nowXg').innerText = gx.toFixed(0);
			document.getElementById('minXg').innerText = minXg.toFixed(0);
			document.getElementById('maxXg').innerText = maxXg.toFixed(0);

			document.getElementById('nowYg').innerText = gy.toFixed(0);
			document.getElementById('minYg').innerText = minYg.toFixed(0);
			document.getElementById('maxYg').innerText = maxYg.toFixed(0);

			document.getElementById('nowZg').innerText = gz.toFixed(0);
			document.getElementById('minZg').innerText = minZg.toFixed(0);
			document.getElementById('maxZg').innerText = maxZg.toFixed(0);

			// UI Tabelle aktualisieren Magneto
			document.getElementById('nowXm').innerText = mx.toFixed(0);
			document.getElementById('minXm').innerText = minXm.toFixed(0);
			document.getElementById('maxXm').innerText = maxXm.toFixed(0);
			
			document.getElementById('nowYm').innerText = my.toFixed(0);
			document.getElementById('minYm').innerText = minYm.toFixed(0);
			document.getElementById('maxYm').innerText = maxYm.toFixed(0);

			document.getElementById('nowZm').innerText = mz.toFixed(0);
			document.getElementById('minZm').innerText = minZm.toFixed(0);
			document.getElementById('maxZm').innerText = maxZm.toFixed(0);

			if (enableChartCheckbox.checked) {
				addData(liveChart , timeStr, 2, [ax, ay, az], [gx, gy, gz]);
				addData(liveChart3, timeStr, 1, [mx, my, mz], []);
			}
			// Logging & Graph
			if(logMe == 1){
				sensorLog.push({ t: timeStr, ax, ay, az, gx, gy, gz, mx, my, mz });
			}
			
			document.getElementById('recordCount').innerText = sensorLog.length;
			
			updateCompass(mx, my);

		});

	} catch (err) {
		console.log("Fehler: " + err);
	}
});

/**
 * @param {Chart} chart - Die Chart.js Instanz
 * @param {String} label - Der Wert für die X-Achse (z.B. Zeitstempel)
 * @param {String} numGroups - Anzahl Gruppen
 * @param {Array} group1 - Array mit 3 Werten [x, y, z] für die linke Achse (+/- 25)
 * @param {Array} group2 - Array mit 3 Werten [x, y, z] für die rechte Achse (+/- 500)
 Beispielaufruf: addData(liveChart, "12:00:01", [10, -5, 2], [300, -150, 420]);
 */
function addData(chart, label, numGroups, group1, group2) {    
    chart.data.labels.push(label);	// 1. Label hinzufügen

    // 2. Daten für die erste Gruppe (Index 0, 1, 2)
    chart.data.datasets[0].data.push(group1[0]); // Beschleunigung X
    chart.data.datasets[1].data.push(group1[1]); // Beschleunigung Y
    chart.data.datasets[2].data.push(group1[2]); // Beschleunigung Z

    // 3. Daten für die zweite Gruppe (Index 3, 4, 5)
	if(numGroups > 1){
		if (Array.isArray(group2) && group2.length > 0) {
			chart.data.datasets[3].data.push(group2[0]); // Gyro X
			chart.data.datasets[4].data.push(group2[1]); // Gyro Y
			chart.data.datasets[5].data.push(group2[2]); // Gyro Z
		} else {
			// Falls leer: null pushen, damit die Linien an dieser Stelle 
			// eine Lücke haben, aber synchron zur Zeitachse bleiben.
			chart.data.datasets[3].data.push(null); // Gyro X
			chart.data.datasets[4].data.push(null); // Gyro Y
			chart.data.datasets[5].data.push(null); // Gyro Z
		}
	}
    
    const maxPoints = 50;			// Optional: Begrenzung der Datenmenge (z.B. nur die letzten 50 Punkte anzeigen)
    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    chart.update('none');			// Chart neu zeichnen (leistungsoptimiert ohne Animation)
}

document.getElementById('downloadBtn').addEventListener('click', () => {
	let csv = "Zeitstempel;aX;aY;aZ;gX;gY;gZ;mX;mY;mZ\n";
	sensorLog.forEach(r => csv += `${r.t};${r.ax};${r.ay};${r.az};${r.gx};${r.gy};${r.gz};${r.mx};${r.my};${r.mz}\n`);
	const blob = new Blob([csv], { type: 'text/csv' });
	const url = URL.createObjectURL(blob);
	const now1 = new Date();
	const a = document.createElement('a');
	a.href = url;
	a.download = `IMU_Log_${now1.toLocaleTimeString()}.csv`;
	a.click();
});

function resetMinMax() {
	minX = minY = minZ = Infinity;
	maxX = maxY = maxZ = -Infinity;
	minXg= minYg= minZg= Infinity;
	maxXg= maxYg= maxZg= -Infinity;
	minXm= minYm= minZm= Infinity;
	maxXm= maxYm= maxZm= -Infinity;
	document.querySelectorAll('.val-min, .val-max').forEach(el => el.innerText = "0.00");
}

function dataStart() {
	sensorLog = [];
	logMe = 1;
	document.getElementById('recordCount').innerText = sensorLog.length;
}

function dataStop() {
	logMe = 0;
}

// --- KOMPASS BERECHNUNG ---
function updateCompass(mx, my) {
	// 1. Winkel berechnen (atan2 gibt Radianten zurück: -PI bis +PI)
	// Wir tauschen my und mx und negieren my, damit 0 Grad Norden ist
	// Dies ist eine vereinfachte Annahme für einen flach liegenden Sensor.
	let angleRad = Math.atan2(my, mx);

	// 2. In Grad umrechnen
	let angleDeg = angleRad * (180 / Math.PI);

	// 3. Auf 0-360 Grad normalisieren (optional, aber schöner für Text)
	if (angleDeg < 0) {
		 angleDeg += 360;
	}

	// 4. Die Nadel rotieren (CSS transform)
	// Wir müssen den Winkel für die CSS Rotation anpassen, damit er zur Grafik passt
	// (atan2 0 Grad ist oft "Osten", wir wollen aber Norden oben haben)
	const rotationOffset = 0; 
	needleWrapper.style.transform = `rotate(${angleDeg + rotationOffset}deg)`;
	
	// Text aktualisieren
	headingValueSpan.innerText = angleDeg.toFixed(0);
}