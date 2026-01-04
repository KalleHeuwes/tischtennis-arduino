/*
    Ermittelt die Sensordaten von Gyroscope, Acceleration und Magnetometer
    Diese werden über Bluetooth in einem String bereitgestellt: ax, ay, az, gx, gy, gz, mx, my, mz
*/

#include <ArduinoBLE.h>
#include <Arduino_BMI270_BMM150.h>

// BLE Definitionen
BLEService              sensorService("1101"); 
BLEStringCharacteristic sensorData("2101", BLERead | BLENotify, 50);

//const float G_TO_MS2 = 9.80665f;
const float thresholda = 0.2;
const float thresholdg = 2;

//float ax_a, ay_a, az_a;
float ax, ay, az;
float mx, my, mz;
float gx, gy, gz;
float lastXa = 0, lastYa = 0, lastZa = 0;
float lastXg = 0, lastYg = 0, lastZg = 0;

void setup() {
  Serial.println("setup");
  Serial.begin(9600);

  pinMode(LED_BUILTIN, OUTPUT);

  if (!IMU.begin()) {
    Serial.println("Fehler: IMU nicht gefunden!");
    while (1);
  }

  if (!BLE.begin()) {
    Serial.println("Fehler: Bluetooth konnte nicht gestartet werden!");
    while (1);
  }

  // BLE Konfiguration
  BLE.setLocalName("Nano33_IMU");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(sensorData);
  BLE.addService(sensorService);
  
  // Startet das Sichtbar-Sein
  BLE.advertise();
  Serial.println("Bluetooth gestartet. Warte auf Verbindung...");
}

void loop() {  
  BLEDevice central = BLE.central();        // Überprüfe ständig auf eine Verbindung

  if (central) {
    digitalWrite(LED_BUILTIN, HIGH);        // LED an bei Verbindung
    Serial.println("Verbunden mit: " + central.address());

    while (central.connected()) {
      if (IMU.accelerationAvailable()) {
        IMU.readGyroscope     (gx, gy, gz);
        IMU.readMagneticField (mx, my, mz);
        IMU.readAcceleration  (ax, ay, az);
        //float ax = ax_a * G_TO_MS2;
        //float ay = ay_a * G_TO_MS2;
        //float az = az_a * G_TO_MS2;

        if (abs(ax - lastXa) > thresholda || abs(ay - lastYa) > thresholda || abs(az - lastZa) > thresholda ||
            abs(gx - lastXg) > thresholdg || abs(gy - lastYg) > thresholdg || abs(gz - lastZg) > thresholdg
            ) {          
          String data = String(ax) + "," + String(ay) + "," + String(az) + "," +
                        String(gx) + "," + String(gy) + "," + String(gz) + "," +
                        String(mx) + "," + String(my) + "," + String(mz);   // Daten als CSV-String formatieren
          sensorData.writeValue(data);                                   // Per Bluetooth senden          
          //Serial.println("Gesendet: " + data);
          lastXa = ax; lastYa = ay; lastZa = az;
          lastXg = gx; lastYg = gy; lastZg = gz;
        }
      }
      // Kurze Pause zur Entlastung des BLE-Stacks
      delay(20);
    }   

    // Wenn die Verbindung getrennt wurde
    digitalWrite(LED_BUILTIN, LOW); // LED aus
    Serial.println("Verbindung getrennt.");
    
    // WICHTIG: Explizit wieder sichtbar werden
    BLE.advertise(); 
    Serial.println("Wieder im Advertising-Modus...");
  }
}