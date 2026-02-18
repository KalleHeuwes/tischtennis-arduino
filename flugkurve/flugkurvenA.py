import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from matplotlib.colors import Normalize

def calculate_trajectory(file_path):
    df = pd.read_csv(file_path, sep=';')
    df['Zeitstempel'] = pd.to_datetime(df['Zeitstempel'], format='%H:%M:%S.%f')
    df['dt'] = df['Zeitstempel'].diff().dt.total_seconds().fillna(0)
    
    num_points = len(df)
    pos = np.zeros((num_points, 3))
    vel = np.zeros((num_points, 3))
    acc_mags = np.zeros(num_points)
    
    # Präziser Bias-Abgleich: Wir nehmen den Durchschnitt der ersten 5 Messwerte als Nullpunkt
    initial_acc = df[['aX', 'aY', 'aZ']].iloc[:5].mean().values
    current_rot = R.from_euler('xyz', [0, 0, 0])
    total_dist = 0.0
    
    for i in range(1, num_points):
        dt = df.loc[i, 'dt']
        if dt <= 0: dt = 0.01 # Fallback für Zeitfehler
        
        # Gyro-Integration
        gyro = np.array([df.loc[i, 'gX'], df.loc[i, 'gY'], df.loc[i, 'gZ']])
        delta_rot = R.from_rotvec(gyro * dt)
        current_rot = current_rot * delta_rot
        
        # Beschleunigung (Offset abziehen)
        acc_raw = np.array([df.loc[i, 'aX'], df.loc[i, 'aY'], df.loc[i, 'aZ']])
        acc_mags[i] = np.linalg.norm(acc_raw)
        
        # Transformation in Welt-Koordinaten
        acc_global = current_rot.apply(acc_raw)
        # Wir ziehen den initialen Bias ab (berücksichtigt die Lage des Sensors beim Start)
        acc_linear = (acc_global - current_rot.apply(initial_acc)) * 9.81
        
        # Rauschfilter (Deadzone): Kleine zittrige Bewegungen ignorieren
        if np.linalg.norm(acc_linear) < 0.5: acc_linear = np.zeros(3)

        # Integration
        vel[i] = vel[i-1] + acc_linear * dt
        # Dämpfung: Verhindert, dass die Geschwindigkeit unendlich weiterwächst (Drift-Korrektur)
        vel[i] *= 0.95 
        
        new_pos = pos[i-1] + vel[i] * dt
        total_dist += np.linalg.norm(new_pos - pos[i-1])
        pos[i] = new_pos
        
    return pos, acc_mags, total_dist

def plot_colored_path(ax, pos, acc_mags, label, cmap_name, norm, total_dist):
    points = pos.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    cmap = plt.get_cmap(cmap_name)
    
    for i in range(len(segments)):
        ax.plot(segments[i,:,0], segments[i,:,1], segments[i,:,2], 
                color=cmap(norm(acc_mags[i])), lw=3, alpha=0.9)
    
    ax.plot([], [], [], color=cmap(0.6), label=f"{label} ({total_dist:.2f} m)", lw=3)

# --- Hauptprogramm ---
pfad_1, acc_1, dist_1 = calculate_trajectory('schlag_1.csv')
pfad_2, acc_2, dist_2 = calculate_trajectory('schlag_2.csv')

norm_global = Normalize(vmin=0.8, vmax=3.0)

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

plot_colored_path(ax, pfad_1, acc_1, 'Schlag 1', 'Blues', norm_global, dist_1)
plot_colored_path(ax, pfad_2, acc_2, 'Schlag 2', 'Oranges', norm_global, dist_2)

# Marker
ax.scatter(0, 0, 0, color='green', s=100, label='Start')
ax.scatter(pfad_1[-1,0], pfad_1[-1,1], pfad_1[-1,2], color='red', marker='X')
ax.scatter(pfad_2[-1,0], pfad_2[-1,1], pfad_2[-1,2], color='red', marker='X')

# --- AUTOMATISCHE SKALIERUNG ---
# Berechnet die Grenzen basierend auf den tatsächlichen Daten
all_pos = np.vstack([pfad_1, pfad_2])
max_val = np.abs(all_pos).max()
ax.set_xlim([-max_val, max_val])
ax.set_ylim([-max_val, max_val])
ax.set_zlim([-max_val, max_val])

ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Z [m]')
plt.legend()
plt.show()