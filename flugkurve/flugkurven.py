import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

def calculate_trajectory(file_path):
    # Daten laden
    df = pd.read_csv(file_path, sep=';')
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], format='%H:%M:%S.%f')
    df['dt'] = df['Zeitstempel'].diff().dt.total_seconds().fillna(0)
    
    num_points = len(df)
    pos = np.zeros((num_points, 3))
    vel = np.zeros((num_points, 3))
    current_rot = R.from_euler('xyz', [0, 0, 0])
    gravity_global = np.array([0, 0, 1.0]) 

    for i in range(1, num_points):
        dt = df.loc[i, 'dt']
        if dt <= 0: continue
        
        # Orientierung (Gyroskop rad/s)
        gyro = np.array([df.loc[i, 'gX'], df.loc[i, 'gY'], df.loc[i, 'gZ']])
        delta_rot = R.from_rotvec(gyro * dt)
        current_rot = current_rot * delta_rot
        
        # Beschleunigung transformieren & Schwerkraft abziehen
        acc_sensor = np.array([df.loc[i, 'aX'], df.loc[i, 'aY'], df.loc[i, 'aZ']])
        acc_global = current_rot.apply(acc_sensor)
        acc_linear = acc_global - gravity_global
        
        # Integration zu Position (in m)
        acc_m_s2 = acc_linear * 9.81
        vel[i] = vel[i-1] + acc_m_s2 * dt
        pos[i] = pos[i-1] + vel[i] * dt
        
    return pos

# --- Hauptprogramm ---

# Beide Flugkurven berechnen
pfad_1 = calculate_trajectory('schlag_1.csv')
pfad_2 = calculate_trajectory('schlag_2.csv')

# 3D Plot erstellen
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Kurve 1 plotten
ax.plot(pfad_1[:, 0], pfad_1[:, 1], pfad_1[:, 2], label='Schlag 1', color='blue', lw=2)
ax.scatter(pfad_1[0,0], pfad_1[0,1], pfad_1[0,2], color='blue', s=50, marker='o') # Start 1

# Kurve 2 plotten
ax.plot(pfad_2[:, 0], pfad_2[:, 1], pfad_2[:, 2], label='Schlag 2', color='orange', lw=2)
ax.scatter(pfad_2[0,0], pfad_2[0,1], pfad_2[0,2], color='orange', s=50, marker='x') # Start 2

# Achsen und Design
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.set_title('Vergleich zweier Schlag-Trajektorien')
ax.legend()

# Skalierung vereinheitlichen
all_data = np.vstack((pfad_1, pfad_2))
limit = np.max(np.abs(all_data))
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-limit, limit)

plt.show()