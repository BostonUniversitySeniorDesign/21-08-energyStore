#include "Wire.h"

extern "C" { 
#include "utility/twi.h"  // from Wire library, so we can do bus scanning
}
#include <Adafruit_INA260.h>
Adafruit_INA260 ina260 = Adafruit_INA260();

/* Used to select I2C MUX */
#define TCAADDR 0x70
void tcaselect(uint8_t i) {
  if (i > 7) return;
 
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

/* RELAYS */
// Relay 1 is for rectifier switch
const int RELAY1_1 = 22;  // [HIGH, Rectifier disconnected]
                          // [LOW, Rectifier connected]
const int RELAY1_2 = 23;  // NOT CONNECTED

// Relay 2 is for battery charge/discharge
const int RELAY2_1 = 52;  // [HIGH, Battery disconnected]
                          // [LOW, Move to RELAY2_2]
const int RELAY2_2 = 53;  // [HIGH, Battery charging]
                          // [LOW, Battery discharging]

/* Variables to store power */
int grid_power;
int charge_power;
int discharge_power;
int home0_power;
int home1_power;
int home2_power;
int home3_power;

/* For state of system */
String input;    // For Serial Input
String battery;  // For Battery State
String grid;     // For Grid State

void setup() {

  /* Set relays as OUTPUT */
  pinMode(RELAY1_1, OUTPUT);
  pinMode(RELAY1_2, OUTPUT);
  pinMode(RELAY2_1, OUTPUT);
  pinMode(RELAY2_2, OUTPUT);

  /* Set all relays off */
  digitalWrite(RELAY1_1, HIGH);
  digitalWrite(RELAY1_2, HIGH);
  grid="OFF";
  digitalWrite(RELAY2_1, HIGH);
  digitalWrite(RELAY2_2, HIGH);
  battery="DISCONNECT";

  /* Wait for Serial to start */
  while (!Serial);
  delay(1000);
 
  /* Open serial link*/
  Wire.begin();
  Serial.begin(115200);
  Serial.println("\nTCAScanner ready!");
  
  for (uint8_t t=0; t<8; t++) {
    tcaselect(t);
    Serial.print("TCA Port #"); Serial.println(t);

    for (uint8_t addr = 0; addr<=127; addr++) {
      if (addr == TCAADDR) continue;
      
      uint8_t data;
      if (! twi_writeTo(addr, &data, 0, 1, 1)) {
         Serial.print("Found I2C 0x");  Serial.println(addr,HEX);
      }
    }
    /* initialize all ina260's */
    if (!ina260.begin()) {
      Serial.println("Couldn't find INA260 chip");
    } else {
      Serial.println("Found INA260 chip");
    } 
  }
  Serial.println("\ndone");
  delay(1000);
}

/* Loop runs repeatedly */
void loop() {
  // Wait for serial input
  while (!Serial.available());

  // Get input
  input = Serial.readString();

  // Cases for commands 
  if (input == "gON") { // Turn Grid ON
      gridON();
      grid="ON";
  
  } else if (input == "gOFF") { // Turn Grid OFF
      gridOFF();
      grid="OFF";

  } else if (input == "bCHARGE") { // CHARGE Battery
      batteryCHARGE();
      battery="CHARGE";

  } else if (input == "bDISCHARGE") { // DISCHARGE Battery
      batteryDISCHARGE();
      battery="DISCHARGE";

  } else if (input == "bDISCONNECT") { //DISCONNECT Battery
      battery="DISCONNECT";
      batteryDISCONNECT();

  }

  /* Read and store power meters */
  tcaselect(0); // Grid Meter
  grid_power = ina260.readPower();
  delay(20);

  tcaselect(1); // Charging Meter
  charge_power = ina260.readPower();
  delay(20);

  tcaselect(2); // Discharge Meter
  discharge_power = ina260.readPower();
  delay(20);

  tcaselect(3); // H0 Meter
  home0_power = ina260.readPower();
  delay(20);

  tcaselect(4); // H1 Meter
  home1_power = ina260.readPower();
  delay(20);

  tcaselect(5); // H2 Meter
  home2_power = ina260.readPower();
  delay(20);

  tcaselect(6); // H3 Meter
  home3_power = ina260.readPower();
  delay(20);

  Serial.println("{\"Home0\": " + String(home0_power) + ", "
                + "\"Home1\": " + String(home1_power) + ", " 
                + "\"Home2\": " + String(home2_power) + ", " 
                + "\"Home3\": " + String(home3_power) + ", " 
                + "\"Grid\": " + String(grid_power) + ", " 
                + "\"Charge\": " + String(charge_power) + ", " 
                + "\"Discharge\": " + String(discharge_power) + ", " 
                + "\"BATTERY\": \"" + battery + "\", " 
                + "\"GRID\": \"" + grid + "\"}");
}



/* GRID FUNCTIONS */
void gridON() {
    digitalWrite(RELAY2_2, HIGH); // Make sure battery not discharging
    digitalWrite(RELAY1_1, LOW);
}
void gridOFF() {
    digitalWrite(RELAY1_1, HIGH);
}
/* BATTERY FUNCTIONS */
void batteryCHARGE() {
    digitalWrite(RELAY2_1, LOW);
    digitalWrite(RELAY2_2, HIGH);
}
void batteryDISCHARGE() {
    gridOFF(); // Turn off grid before discharging battery
    digitalWrite(RELAY2_1, LOW);
    digitalWrite(RELAY2_2, LOW);
}
void batteryDISCONNECT() {
    digitalWrite(RELAY2_1, HIGH);
    digitalWrite(RELAY2_2, HIGH);
}
