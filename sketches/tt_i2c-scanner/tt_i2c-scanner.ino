#include <Wire.h>

void scanBus(TwoWire &bus, String busName) {
  Serial.println("Scanne " + busName + "...");
  byte error, address;
  int nDevices = 0;

  for (address = 1; address < 127; address++) {
    bus.beginTransmission(address);
    error = bus.endTransmission();

    if (error == 0) {
      Serial.print("Gerät gefunden bei Adresse 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      Serial.println(" !");
      nDevices++;
    } else if (error == 4) {
      Serial.print("Unbekannter Fehler bei Adresse 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }
  if (nDevices == 0) Serial.println("Keine I2C Geräte gefunden an " + busName + "\n");
  else Serial.println("Scan beendet.\n");
}

void setup() {
  Serial.begin(115200);
  while (!Serial); // Warten auf Monitor
  Serial.println("\nI2C Scanner startet...");

  Wire.begin();  // Externer Bus
  Wire1.begin(); // Interner Bus (wichtig für Nano 33 BLE)

  scanBus(Wire, "Wire (Extern)");
  scanBus(Wire1, "Wire1 (Intern)");
}

void loop() {}