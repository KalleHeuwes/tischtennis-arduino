#include "Arduino_BMI270_BMM150.h"
#include <ArduinoBLE.h>
#include <Wire.h>

// BLE Definitionen
BLEService              sensorService("1101"); 
BLEStringCharacteristic sensorData("2101", BLERead | BLENotify, 80);

float maxG = 0.0;
const uint8_t BMI270_ADDR = 0x68; 

void setup() {
  Serial.begin(115200);
  unsigned long startWait = millis();
  while (!Serial && millis() - startWait < 3000);

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

        // Teste, ob Library Skalierung anpasst. Falls Schläger im Stillstand nur 0.25 anzeigt, hier mit 4 multiplizieren.
        float currentG = sqrt(x * x + y * y + z * z) * 4;
        unsigned long currentMillis = millis(); // Aktueller Zeitstempel
        String timeString = formatMillis(currentMillis);

        if(currentG > 2){
          if (currentG > maxG) {
            maxG = currentG;
            Serial.print("Neuer Peak: " + String(maxG) + " g");
            String data = "PERFORMANCE:" + String(timeString) + "," + String(currentMillis) + "," + String(maxG) + "," + String(x) + "," + String(y) + "," + String(z);
            sensorData.writeValue(data);                                   // Per Bluetooth senden        
          } 
        }
        if (currentG < 1.2 && currentG < maxG) {
            sensorData.writeValue("PERFORMANCE:zurückgesetzt," + String(currentG) + "," + String(maxG)); 
            maxG = 0; // Aktueller Wert sinkt wieder -> maxG zurücksetzen, um für den nächsten Schlag bereit zu sein.
        }
      }      
      delay(20);    // Kurze Pause zur Entlastung des BLE-Stacks
    }
  }
}

String formatMillis(unsigned long ms) {
  unsigned long totalSeconds = ms / 1000;
  
  int milliseconds = ms % 1000;
  int seconds = totalSeconds % 60;
  int minutes = (totalSeconds / 60) % 60;
  int hours = (totalSeconds / 3600); // Stunden können hier über 24 hinausgehen

  char buffer[20];
  // Format: HH:MM:SS.mmm (mit führenden Nullen)
  sprintf(buffer, "%02d:%02d:%02d.%03d", hours, minutes, seconds, milliseconds);
  
  return String(buffer);
}