import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

# 1. Daten laden
# Wir nutzen sep=';' für deine CSV-Struktur
df = pd.read_csv('schlag_daten.csv', sep=';')

# Zeitstempel umwandeln und Delta t (Zeitdifferenz) berechnen
df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], format='%H:%M:%S.%f')
df['dt'] = df['Zeitstempel'].diff().dt.total_seconds().fillna(0)

# 2. Vorbereitung der Arrays
num_points = len(df)
pos = np.zeros((num_points, 3))  # Position (x, y, z)
vel = np.zeros((num_points, 3))  # Geschwindigkeit (vx, vy, vz)

# Orientierung initialisieren (als Einheits-Rotation)
current_rot = R.from_euler('xyz', [0, 0, 0])

# Annahme: Deine acc-Werte sind in "g" (Erdanziehung)
# Wir definieren den Schwerkraftvektor im globalen System
gravity_global = np.array([0, 0, 1.0]) 

# 3. Die "Schleife" durch die Bewegung
for i in range(1, num_points):
    dt = df.loc[i, 'dt']
    if dt <= 0: continue
    
    # --- A) Orientierung berechnen ---
    # Gyroskop-Werte (angenommen: rad/s. Falls Grad/s: np.radians nutzen)
    gyro = np.array([df.loc[i, 'gX'], df.loc[i, 'gY'], df.loc[i, 'gZ']])
    
    # Kleine Rotation für diesen Zeitschritt berechnen
    delta_rot = R.from_rotvec(gyro * dt)
    current_rot = current_rot * delta_rot
    
    # --- B) Beschleunigung verarbeiten ---
    acc_sensor = np.array([df.loc[i, 'aX'], df.loc[i, 'aY'], df.loc[i, 'aZ']])
    
    # Beschleunigung vom Sensor-System ins globale System drehen
    acc_global = current_rot.apply(acc_sensor)
    
    # Schwerkraft abziehen, um reine Bewegung zu erhalten
    acc_linear = acc_global - gravity_global
    
    # Umrechnung von g in m/s²
    acc_m_s2 = acc_linear * 9.81
    # acc_m_s2 = acc_linear
    
    # --- C) Integration (Trapez-Regel) ---
    vel[i] = vel[i-1] + acc_m_s2 * dt
    pos[i] = pos[i-1] + vel[i] * dt

# 4. 3D-Plot erstellen
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Trajektorie plotten
ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], label='Flugkurve des Schlags', color='blue', lw=2)

# Start- und Endpunkt markieren
ax.scatter(pos[0,0], pos[0,1], pos[0,2], color='green', s=100, label='Start')
ax.scatter(pos[-1,0], pos[-1,1], pos[-1,2], color='red', s=100, label='Ende')

# Achsenbeschriftung
ax.set_xlabel('X (Meter)')
ax.set_ylabel('Y (Meter)')
ax.set_zlabel('Z (Meter)')
ax.set_title('Visualisierung des Schlags (Arduino Nano 33 BLE Sense)')
ax.legend()

# Achsen gleich skalieren (wichtig für korrekte Optik)
limit = np.max(np.abs(pos))
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit, limit)

plt.show()