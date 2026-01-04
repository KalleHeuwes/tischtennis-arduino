import asyncio
import struct
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bleak import BleakClient
from scipy.spatial.transform import Rotation as R

# --- KONFIGURATION ---
CHARACTERISTIC_UUID = "2101"
ADDRESS = "f0:9e:4a:f0:1c:06"  # <--- HIER DEINE ADRESSE EINTRAGEN
RECORD_SECONDS = 3

raw_packets = []

def notification_handler(sender, data):
    # Entpackt 6 Floats (24 Bytes)
    floats = struct.unpack('6f', data)
    raw_packets.append(floats)

async def capture_live_data():
    print(f"Suche Verbindung zu {ADDRESS}...")
    async with BleakClient(ADDRESS) as client:
        print("Verbunden! Aufnahme startet in 3, 2, 1...")
        await asyncio.sleep(1)
        print("--- JETZT SCHLAGEN! ---")
        
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        await asyncio.sleep(RECORD_SECONDS)
        await client.stop_notify(CHARACTERISTIC_UUID)
        
        print(f"Aufnahme beendet. {len(raw_packets)} Datenpunkte empfangen.")

def process_and_plot(data):
    if len(data) < 10:
        print("Zu wenig Daten empfangen!")
        return

    # In DataFrame umwandeln
    df = pd.DataFrame(data, columns=['accX', 'accY', 'accZ', 'gyrX', 'gyrY', 'gyrZ'])
    
    # Zeitintervall schätzen (basierend auf 100Hz im Arduino-Code)
    dt = 0.01 
    
    num_points = len(df)
    pos = np.zeros((num_points, 3))
    vel = np.zeros((num_points, 3))
    current_rot = R.from_euler('xyz', [0, 0, 0])
    gravity_global = np.array([0, 0, 1.0])

    for i in range(1, num_points):
        # Orientierung aus Gyro (rad/s)
        gyro = np.array([df.iloc[i]['gyrX'], df.iloc[i]['gyrY'], df.iloc[i]['gyrZ']])
        delta_rot = R.from_rotvec(gyro * dt)
        current_rot = current_rot * delta_rot
        
        # Beschleunigung transformieren
        acc_sensor = np.array([df.iloc[i]['accX'], df.iloc[i]['accY'], df.iloc[i]['accZ']])
        acc_global = current_rot.apply(acc_sensor)
        
        # Schwerkraft abziehen & integrieren
        acc_linear = (acc_global - gravity_global) * 9.81
        vel[i] = vel[i-1] + acc_linear * dt
        pos[i] = pos[i-1] + vel[i] * dt

    # Plotting
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(pos[:, 0], pos[:, 1], pos[:, 2], label='Live Schlagkurve', lw=2, color='red')
    ax.scatter(pos[0,0], pos[0,1], pos[0,2], color='green', label='Start')
    ax.set_title("Live-Auswertung")
    ax.legend()
    plt.show()

# Hauptablauf
if __name__ == "__main__":
    asyncio.run(capture_live_data())
    process_and_plot(raw_packets)