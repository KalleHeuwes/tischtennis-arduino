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

const maxPointsInGraph = 60;
const ctx = document.getElementById('liveChart').getContext('2d');
const liveChart = new Chart(ctx, {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{ label: 'X', borderColor: '#ff5252', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Y', borderColor: '#4caf50', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Z', borderColor: '#2196f3', data: [], borderWidth: 2, pointRadius: 0, fill: false }
		]
	},
	options: {
		responsive: true,
		maintainAspectRatio: false,
		animation: false,
		scales: {
			y: { min: -25, max: 25 },
			x: { display: false }
		}
	}
});
const ctx2 = document.getElementById('liveChart2').getContext('2d');
const liveChart2 = new Chart(ctx2, {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{ label: 'X', borderColor: '#ff5252', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Y', borderColor: '#4caf50', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Z', borderColor: '#2196f3', data: [], borderWidth: 2, pointRadius: 0, fill: false }
		]
	},
	options: {
		responsive: true,
		maintainAspectRatio: false,
		animation: false,
		scales: {
			y: { min: -500, max: 500 },
			x: { display: false }
		}
	}
});
const ctx3 = document.getElementById('liveChart3').getContext('2d');
const liveChart3 = new Chart(ctx3, {
	type: 'line',
	data: {
		labels: [],
		datasets: [
			{ label: 'X', borderColor: '#ff5252', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Y', borderColor: '#4caf50', data: [], borderWidth: 2, pointRadius: 0, fill: false },
			{ label: 'Z', borderColor: '#2196f3', data: [], borderWidth: 2, pointRadius: 0, fill: false }
		]
	},
	options: {
		responsive: true,
		maintainAspectRatio: false,
		animation: false,
		scales: {
			y: { min: -50, max: 50 },
			x: { display: false }
		}
	}
});

const SERVICE_UUID = 0x1101;
const CHARACTERISTIC_UUID = 0x2101;


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
		document.getElementById('connectBtn').disabled = true;
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


			// Logging & Graph
			sensorLog.push({ t: timeStr, ax, ay, az, gx, gy, gz, mx, my, mz });
			document.getElementById('recordCount').innerText = sensorLog.length;

			liveChart.data.labels.push(timeStr);
			liveChart.data.datasets[0].data.push(ax);
			liveChart.data.datasets[1].data.push(ay);
			liveChart.data.datasets[2].data.push(az);

			if (liveChart.data.labels.length > maxPointsInGraph) {
				liveChart.data.labels.shift();
				liveChart.data.datasets.forEach(d => d.data.shift());
			}
			liveChart.update('none');				
			
			liveChart2.data.labels.push(timeStr);
			liveChart2.data.datasets[0].data.push(gx);
			liveChart2.data.datasets[1].data.push(gy);
			liveChart2.data.datasets[2].data.push(gz);

			if (liveChart2.data.labels.length > maxPointsInGraph) {
				liveChart2.data.labels.shift();
				liveChart2.data.datasets.forEach(d => d.data.shift());
			}
			liveChart2.update('none');			
			
			liveChart3.data.labels.push(timeStr);
			liveChart3.data.datasets[0].data.push(mx);
			liveChart3.data.datasets[1].data.push(my);
			liveChart3.data.datasets[2].data.push(mz);

			if (liveChart3.data.labels.length > maxPointsInGraph) {
				liveChart3.data.labels.shift();
				liveChart3.data.datasets.forEach(d => d.data.shift());
			}
			liveChart3.update('none');
		});

	} catch (err) {
		console.log("Fehler: " + err);
	}
});

document.getElementById('downloadBtn').addEventListener('click', () => {
	let csv = "Zeitstempel;aX;aY;aZ;gX;gY;gZ;mX;mY;mZ\n";
	sensorLog.forEach(r => csv += `${r.t};${r.ax};${r.ay};${r.az};${r.gx};${r.gy};${r.gz};${r.mx};${r.my};${r.mz}\n`);
	const blob = new Blob([csv], { type: 'text/csv' });
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	//a.download = `IMU_Log_${new Date().getTime()}.csv`;
	a.download = `IMU_Log.csv`;
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
	document.getElementById('recordCount').innerText = sensorLog.length;
}