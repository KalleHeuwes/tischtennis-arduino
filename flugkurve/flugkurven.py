import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from matplotlib.colors import Normalize

def calculate_trajectory(file_path):
    # Daten laden
    df = pd.read_csv(file_path, sep=';')
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], format='%H:%M:%S.%f')
    df['dt'] = df['Zeitstempel'].diff().dt.total_seconds().fillna(0)
    
    num_points = len(df)
    pos = np.zeros((num_points, 3))
    vel = np.zeros((num_points, 3))
    acc_mags = np.zeros(num_points)
    
    # Start-Rotation: Wir nehmen an, der Sensor startet flach
    current_rot = R.from_euler('xyz', [0, 0, 0])
    
    for i in range(1, num_points):
        dt = df.loc[i, 'dt']
        if dt <= 0: continue
        
        # 1. Gyroskop-Daten für Rotation nutzen
        gyro = np.array([df.loc[i, 'gX'], df.loc[i, 'gY'], df.loc[i, 'gZ']])
        delta_rot = R.from_rotvec(gyro * dt)
        current_rot = current_rot * delta_rot
        
        # 2. Beschleunigung im Sensor-System
        acc_sensor = np.array([df.loc[i, 'aX'], df.loc[i, 'aY'], df.loc[i, 'aZ']])
        acc_mags[i] = np.linalg.norm(acc_sensor) # Magnitude für Farbe speichern
        
        # 3. In globales System drehen und Schwerkraft (1G) abziehen
        acc_global = current_rot.apply(acc_sensor)
        acc_linear = acc_global - np.array([0, 0, 1.0]) 
        
        # 4. Integration zu Geschwindigkeit und Position
        acc_m_s2 = acc_linear * 9.81
        vel[i] = vel[i-1] + acc_m_s2 * dt
        pos[i] = pos[i-1] + vel[i] * dt
        
    return pos, acc_mags

def plot_colored_path(ax, pos, acc_mags, label, cmap_name, norm):
    points = pos.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    cmap = plt.get_cmap(cmap_name)
    
    # Segmente einzeln zeichnen für den Farbverlauf
    for i in range(len(segments)):
        ax.plot(segments[i,:,0], segments[i,:,1], segments[i,:,2], 
                color=cmap(norm(acc_mags[i])), lw=3, alpha=0.9)
    
    # Dummy-Linie für die Legende (repräsentative Farbe der Map)
    ax.plot([], [], [], color=cmap(0.6), label=label, lw=3)

# --- Hauptprogramm ---

pfad_1, acc_1 = calculate_trajectory('schlag_1.csv')
pfad_2, acc_2 = calculate_trajectory('schlag_2.csv')

# Gemeinsame Normalisierung für beide Kurven (0.5G bis 4G)
# Damit bedeutet "Dunkelblau" bei beiden Kurven die gleiche Kraft
norm_global = Normalize(vmin=0.5, vmax=4.0)

fig = plt.figure(figsize=(14, 9))
ax = fig.add_subplot(111, projection='3d')

# Pfade zeichnen
plot_colored_path(ax, pfad_1, acc_1, 'Schlag 1 (Datei 1)', 'Blues', norm_global)
plot_colored_path(ax, pfad_2, acc_2, 'Schlag 2 (Datei 2)', 'Oranges', norm_global)

# Start- und Endmarkierungen
ax.scatter(0, 0, 0, color='green', s=150, label='Startpunkt (0,0,0)', edgecolors='white', zorder=10)
ax.scatter(pfad_1[-1,0], pfad_1[-1,1], pfad_1[-1,2], color='red', s=100, marker='X')
ax.scatter(pfad_2[-1,0], pfad_2[-1,1], pfad_2[-1,2], color='red', s=100, marker='X', label='Endpunkte')

# Achsenbeschriftung und feste Skalierung
ax.set_xlabel('X [m] (Seitlich)')
ax.set_ylabel('Y [m] (Vorwärts)')
ax.set_zlabel('Z [m] (Höhe)')

# Optionale feste Skalierung für besseren Vergleich (Werte ggf. anpassen)
# ax.set_xlim([-1, 1])
# ax.set_ylim([0, 2])
# ax.set_zlim([-1, 1])

ax.set_title('3D Flugkurven Analyse\n(Dunklere Farbe = Höhere Beschleunigung/Impact)')

# Colorbar zur Erklärung der G-Kräfte (beispielhaft für Blau)
sm = plt.cm.ScalarMappable(cmap='Blues', norm=norm_global)
cbar = fig.colorbar(sm, ax=ax, shrink=0.5, aspect=10, pad=0.1)
cbar.set_label('Beschleunigung [G]')

ax.legend(loc='upper left')
plt.show()