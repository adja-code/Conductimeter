
#include <Adafruit_MAX31865.h>

// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13);


// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define RREF      430.0
// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000
#define RNOMINAL  100.0

void setup() {
  Serial.begin(115200);
//  Serial.println("Adafruit MAX31865 PT100 Sensor Test!");

  thermo.begin(MAX31865_4WIRE);  // set to 2WIRE or 4WIRE as necessary
}


void loop() {
 //int tension = analogRead(A0);
  float tension = analogRead(A0)* 5.0 / 1023.0 ;
  uint16_t rtd = thermo.readRTD();
  Serial.print(thermo.temperature(RNOMINAL, RREF));
  Serial.print(",");
  Serial.println(tension);
  //Serial.println(",");
  //Serial.print(tension);
  delay(10 );
}
