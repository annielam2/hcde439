// A6 "Firefly Jar" firmware
// Sends the joystick, photoresistor and joystick button to the web page,
// and lights the RGB LED in whatever color the web page tells it to.

// Analog pin wired to the joystick's left/right wiper (VRx)
const int JOY_X_PIN = A0;
// Analog pin wired to the joystick's up/down wiper (VRy)
const int JOY_Y_PIN = A1;
// Analog pin wired to the middle of the photoresistor / 10k voltage divider
const int LIGHT_PIN = A2;
// Digital pin wired to the joystick's push button (SW)
const int BUTTON_PIN = 2;
// PWM pin driving the RGB LED's red leg through a 220 ohm resistor
const int RED_PIN = 9;
// PWM pin driving the RGB LED's green leg through a 220 ohm resistor
const int GREEN_PIN = 10;
// PWM pin driving the RGB LED's blue leg through a 220 ohm resistor
const int BLUE_PIN = 11;

// How often (in milliseconds) to send sensor readings to the web page: 20 times a second
const unsigned long SEND_INTERVAL = 50;
// The millis() time when readings were last sent
unsigned long lastSend = 0;

// Red brightness (0-255) most recently requested by the web page
int jarRed = 0;
// Green brightness (0-255) most recently requested by the web page
int jarGreen = 0;
// Blue brightness (0-255) most recently requested by the web page
int jarBlue = 0;

// setup() runs once when the board powers on or resets
void setup() {
  // Open serial at 9600 baud; the web page must use the same speed
  Serial.begin(9600);
  // Only wait up to 20 ms for the rest of a number so loop() never stalls for long
  Serial.setTimeout(20);
  // Use the Arduino's built-in pull-up resistor so the button reads HIGH until pressed
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  // Make the red LED pin an output
  pinMode(RED_PIN, OUTPUT);
  // Make the green LED pin an output
  pinMode(GREEN_PIN, OUTPUT);
  // Make the blue LED pin an output
  pinMode(BLUE_PIN, OUTPUT);
}

// loop() runs over and over forever
void loop() {
  // ---- Web -> Arduino: receive a color as text like "255,200,40\n" ----
  // Only try to read if at least one character has arrived from the web page
  if (Serial.available() > 0) {
    // Read the first number in the message (red)
    int r = Serial.parseInt();
    // Read the second number in the message (green)
    int g = Serial.parseInt();
    // Read the third number in the message (blue)
    int b = Serial.parseInt();
    // Only accept the color if the message ends with a newline, i.e. it arrived complete
    if (Serial.read() == '\n') {
      // Store red, clamped to the 0-255 range analogWrite accepts
      jarRed = constrain(r, 0, 255);
      // Store green, clamped to 0-255
      jarGreen = constrain(g, 0, 255);
      // Store blue, clamped to 0-255
      jarBlue = constrain(b, 0, 255);
    }
  }

  // ---- Make the LED glow like a firefly ----
  // Read the current time in milliseconds
  unsigned long now = millis();
  // Brightness multiplier that gently pulses between 0.55 and 1.0 about every 1.9 s (2*pi*300 ms)
  float glow = 0.775 + 0.225 * sin(now / 300.0);
  // Set the red brightness: requested color times the pulse
  analogWrite(RED_PIN, (int)(jarRed * glow));
  // Set the green brightness: requested color times the pulse
  analogWrite(GREEN_PIN, (int)(jarGreen * glow));
  // Set the blue brightness: requested color times the pulse
  analogWrite(BLUE_PIN, (int)(jarBlue * glow));

  // ---- Arduino -> Web: send "x,y,light,button\n" every 50 ms ----
  // Only send once at least SEND_INTERVAL ms have passed since the last send
  if (now - lastSend >= SEND_INTERVAL) {
    // Remember when this send happened
    lastSend = now;
    // Send the joystick's left/right reading (0-1023, about 512 at rest)
    Serial.print(analogRead(JOY_X_PIN));
    // Comma separates the values so the web page can split them apart
    Serial.print(",");
    // Send the joystick's up/down reading (0-1023, about 512 at rest)
    Serial.print(analogRead(JOY_Y_PIN));
    // Comma separator
    Serial.print(",");
    // Send the light reading (higher = brighter room, lower = darker)
    Serial.print(analogRead(LIGHT_PIN));
    // Comma separator
    Serial.print(",");
    // Send 1 if the button is pressed (pin pulled LOW) or 0 if not, then end the line
    Serial.println(digitalRead(BUTTON_PIN) == LOW ? 1 : 0);
  }
}
