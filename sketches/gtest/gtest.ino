#include "Arduino_BMI270_BMM150.h"
#include <Wire.h>

float maxG = 0.0;
const uint8_t BMI270_ADDR = 0x68; // Standard I2C Adresse

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Verbindung steht!");

  // 1. Normaler Start der Library
  if (!IMU.begin()) {
    Serial.println("Fehler beim Initialisieren!");
    while (1);
  }

  // 2. Direkter I2C-Zugriff um den Range auf 16g zu zwingen
  // Register 0x41 ist ACC_CONF (beim BMI270 steuert das auch den Range)
  // Wir setzen den Range auf 16g (Bit 0 & 1 auf 11 -> 0x03)
  
  Wire.beginTransmission(BMI270_ADDR);
  Wire.write(0x41); // Register-Adresse für ACC_CONF / RANGE
  Wire.write(0x03); // Wert für 16g (und Standard ODR)
  if (Wire.endTransmission() == 0) {
    Serial.println("Hardware-Register erfolgreich auf 16g umgestellt!");
  } else {
    Serial.println("Fehler: I2C-Schreibzugriff fehlgeschlagen.");
  }
}

void loop() {
  float x, y, z;
  Serial.print("loop");

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);

    // Vektor-Betrag berechnen (Gesamtbeschleunigung)
    float currentG = sqrt(x * x + y * y + z * z);

    // Nur bei neuem Rekordwert ausgeben
    if (currentG > maxG) {
      maxG = currentG;
      Serial.print("Neuer Schläger-Peak: ");
      Serial.print(maxG);
      Serial.println(" g");
    }
  }

  // Kleiner Reset-Check: Wenn du 'r' im Seriellen Monitor sendest, wird der Peak genullt
  if (Serial.available() > 0) {
    if (Serial.read() == 'r') {
      maxG = 0;
      Serial.println("--- Peak zurückgesetzt ---");
    }
  }
}