// Pin for the red LED
const int RED = 9;
// Pin for the green LED
const int GREEN = 10;
// Pin for the yellow LED (this one fades, so it must be a PWM pin)
const int YELLOW = 11;
// Pin the button is connected to
const int BUTTON = 2;

// setup() runs once when the Arduino starts
void setup() {
  // Set the red LED pin as an output
  pinMode(RED, OUTPUT);
  // Set the green LED pin as an output
  pinMode(GREEN, OUTPUT);
  // Set the yellow LED pin as an output
  pinMode(YELLOW, OUTPUT);
  // Set the button pin as an input
  pinMode(BUTTON, INPUT);
}

// loop() runs over and over forever
void loop() {
  // Check if the button is pressed (HIGH) or not (LOW)
  if (digitalRead(BUTTON) == HIGH) {
    // Turn the red LED on
    digitalWrite(RED, HIGH);
    // Turn the green LED on
    digitalWrite(GREEN, HIGH);
    // Fade the yellow LED up: brightness goes from 0 to 255
    for (int brightness = 0; brightness <= 255; brightness++) {
      // Set the yellow LED to this brightness
      analogWrite(YELLOW, brightness);
      // Wait 4 ms so the fade is slow enough to see
      delay(4);
    }
    // Fade the yellow LED back down: brightness goes from 255 to 0
    for (int brightness = 255; brightness >= 0; brightness--) {
      // Set the yellow LED to this brightness
      analogWrite(YELLOW, brightness);
      // Wait 4 ms so the fade is slow enough to see
      delay(4);
    }
  // If the button is not pressed
  } else {
    // Turn the red LED off
    digitalWrite(RED, LOW);
    // Turn the green LED off
    digitalWrite(GREEN, LOW);
  }
}
