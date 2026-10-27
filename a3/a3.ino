// Analog pin connected to V-measure, the middle of the photoresistor / 10k voltage divider
const int SENSOR = A0;
// Red NIGHT LED (on when the room is dark)
const int RED = 9;
// Yellow lamp LED (fades with PWM, so it must be on a PWM pin ~)
const int LAMP = 11;

// setup() runs once when the Arduino starts
void setup() {
  // Start serial communication at 9600 baud so readings show in the Serial Monitor
  Serial.begin(9600);
  // Set the red LED pin as an output
  pinMode(RED, OUTPUT);
  // Set the lamp LED pin as an output
  pinMode(LAMP, OUTPUT);
}

// loop() runs over and over forever
void loop() {
  // Read V-measure as 0-1023 (0-5 V): about 170 when covered (dark), 850 under a flashlight (bright)
  int light = analogRead(SENSOR);
  // Keep the reading between 170 and 850 so map() never goes below 0 or above 255
  int clamped = constrain(light, 170, 850);
  // Map dark (170) to full brightness (255) and bright (850) to off (0): the darker the room, the brighter the lamp
  int brightness = map(clamped, 170, 850, 255, 0);
  // Set the lamp LED's brightness with PWM
  analogWrite(LAMP, brightness);

  // If the reading is below 400 (about 1.96 V, a dim room at dusk)...
  if (light < 400) {
    // ...it's night, so turn the red LED on
    digitalWrite(RED, HIGH);
  // Otherwise there is enough daylight
  } else {
    // Turn the red LED off
    digitalWrite(RED, LOW);
  }

  // Print a label for the light level
  Serial.print("Room light level: ");
  // Print the reading and start a new line
  Serial.println(light);
  // Wait 100 ms, so there are 10 readings per second
  delay(100);
}