
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