import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize

def calculate_trajectory(file_path):
    df = pd.read_csv(file_path, sep=';')
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], format='%H:%M:%S.%f')
    df['dt'] = df['Zeitstempel'].diff().dt.total_seconds().fillna(0)
    
    num_points = len(df)
    pos = np.zeros((num_points, 3))
    vel = np.zeros((num_points, 3))
    acc_mags = np.zeros(num_points)
    
    current_rot = R.from_euler('xyz', [0, 0, 0])
    
    for i in range(1, num_points):
        dt = df.loc[i, 'dt']
        if dt <= 0: continue
        
        gyro = np.array([df.loc[i, 'gX'], df.loc[i, 'gY'], df.loc[i, 'gZ']])
        delta_rot = R.from_rotvec(gyro * dt)
        current_rot = current_rot * delta_rot
        
        acc_sensor = np.array([df.loc[i, 'aX'], df.loc[i, 'aY'], df.loc[i, 'aZ']])
        acc_mags[i] = np.linalg.norm(acc_sensor)
        
        acc_global = current_rot.apply(acc_sensor)
        acc_linear = acc_global - np.array([0, 0, 1.0]) 
        acc_m_s2 = acc_linear * 9.81
        
        vel[i] = vel[i-1] + acc_m_s2 * dt
        pos[i] = pos[i-1] + vel[i] * dt
        
    return pos, acc_mags

def plot_colored_path(ax, pos, acc_mags, label, cmap_name):
    points = pos.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Gemeinsame Normalisierung für die G-Kraft (z.B. 0 bis 5 G)
    norm = Normalize(vmin=0.5, vmax=4.0)
    cmap = plt.get_cmap(cmap_name)
    
    # Segmente zeichnen
    for i in range(len(segments)):
        ax.plot(segments[i,:,0], segments[i,:,1], segments[i,:,2], 
                color=cmap(norm(acc_mags[i])), lw=3, alpha=0.8)
    
    # DUMMY-PLOT für die Legende (einzelner Punkt/Linie in der Hauptfarbe)
    ax.plot([], [], [], color=cmap(0.7), label=label, lw=3)
    
    return norm, cmap

# --- Hauptprogramm ---

pfad_1, acc_1 = calculate_trajectory('schlag_1.csv')
pfad_2, acc_2 = calculate_trajectory('schlag_2.csv')

fig = plt.figure(figsize=(14, 9))
ax = fig.add_subplot(111, projection='3d')

# Pfade plotten und Rückgabewerte für Colorbar speichern
norm_1, cmap_1 = plot_colored_path(ax, pfad_1, acc_1, 'Schlag 1 (Blau)', 'Blues')
norm_2, cmap_2 = plot_colored_path(ax, pfad_2, acc_2, 'Schlag 2 (Orange)', 'Oranges')

# Start/Ende Markierungen
ax.scatter(0, 0, 0, color='green', s=150, label='Gemeinsamer Start', edgecolors='white')
ax.scatter(pfad_1[-1,0], pfad_1[-1,1], pfad_1[-1,2], color='red', s=100, marker='X')
ax.scatter(pfad_2[-1,0], pfad_2[-1,1], pfad_2[-1,2], color='red', s=100, marker='X', label='Endpunkte')

# Colorbar hinzufügen (Beispiel für Schlag 1)
sm = plt.cm.ScalarMappable(cmap=cmap_1, norm=norm_1)
cbar = fig.colorbar(sm, ax=ax, shrink=0.5, aspect=10, pad=0.1)
cbar.set_label('Beschleunigung [G]')

ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Z [m]')
ax.set_title('Vergleich Flugkurven: Schlag 1 vs Schlag 2')

# Legende anzeigen
ax.legend(loc='upper left')

plt.show()