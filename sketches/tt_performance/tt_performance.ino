#include "Arduino_BMI270_BMM150.h"
#include <ArduinoBLE.h>
#include <Wire.h>

// BLE Definitionen
BLEService              sensorService("1101"); 
BLEStringCharacteristic sensorData("2101", BLERead | BLENotify, 50);

float maxG = 0.0;
const uint8_t BMI270_ADDR = 0x68; 

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // 1. Initialisierung der Library
  if (!IMU.begin()) {
    Serial.println("Fehler: IMU konnte nicht gestartet werden.");
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

  // 2. Umstellen auf 16g über Wire1
  // Wir nutzen Wire1, da der Scanner dort den Sensor gefunden hat.
  Wire1.beginTransmission(BMI270_ADDR);
  Wire1.write(0x41); // Register ACC_RANGE
  Wire1.write(0x03); // 0x03 entspricht +/- 16g
  
  if (Wire1.endTransmission() == 0) {
    Serial.println("Erfolg: Sensor auf 16g Messbereich umgestellt!");
  } else {
    Serial.println("Fehler: Kommunikation auf Wire1 fehlgeschlagen.");
  }
}

void loop() {
  BLEDevice central = BLE.central();        // Überprüfe ständig auf eine Verbindung
  float x, y, z;

  if (central) {
    Serial.println("Verbunden mit: " + central.address());
    while (central.connected()) {
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(x, y, z);

        // WICHTIG: Teste, ob die Library die Skalierung anpasst.
        // Falls der Schläger im Stillstand nur 0.25 anzeigt, müssen wir hier mit 4 multiplizieren.
        float currentG = sqrt(x * x + y * y + z * z) * 4;

        if (currentG > maxG) {
          maxG = currentG;
          Serial.print("Neuer Peak: ");
          Serial.print(maxG);
          Serial.println(" g");
          String data = "Neuer Peak in g," + String(maxG);   // Daten als CSV-String formatieren
          sensorData.writeValue(data);                                   // Per Bluetooth senden        
        }
      }

      // Kurze Pause zur Entlastung des BLE-Stacks
      delay(20);
    }
  }
}