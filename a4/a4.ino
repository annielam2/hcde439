// Include the IRremote library (install "IRremote" v4.x in the Library Manager); it decodes the remote's button signals
#include <IRremote.hpp>
// Include the Servo library (built in); it sends the pulses that set the servo's angle
#include <Servo.h>

// IR receiver's signal pin (OUT / Y) is wired to digital pin 11
const int IR_PIN = 11;
// Servo's orange signal wire is wired to digital pin 9
const int SERVO_PIN = 9;
// Feedback LED (with a 220 ohm resistor) is wired to digital pin 7
const int LED_PIN = 7;

// Create a Servo object to control the servo motor
Servo myServo;

// setup() runs once when the Arduino starts
void setup() {
  // Start serial at 9600 baud so button codes show in the Serial Monitor
  Serial.begin(9600);
  // Start the IR receiver on pin 11
  IrReceiver.begin(IR_PIN);
  // Connect the servo to pin 9
  myServo.attach(SERVO_PIN);
  // Set the LED pin as an output
  pinMode(LED_PIN, OUTPUT);
  // Start the servo in the middle (90 degrees)
  myServo.write(90);
}

// loop() runs over and over forever
void loop() {
  // Check if the IR receiver has decoded a button press
  if (IrReceiver.decode()) {
    // Get the button's command code (Elegoo remote: 1 = 0x0C, 2 = 0x18, 3 = 0x5E)
    int code = IrReceiver.decodedIRData.command;
    // Print the code in hex so I can check which button was pressed
    Serial.println(code, HEX);

    // Button 1 pressed...
    if (code == 0x0C) {
      // ...turn the servo all the way to one side (0 degrees)
      myServo.write(0);
    // Button 2 pressed...
    } else if (code == 0x18) {
      // ...turn the servo to the middle (90 degrees)
      myServo.write(90);
    // Button 3 pressed...
    } else if (code == 0x5E) {
      // ...turn the servo all the way to the other side (180 degrees)
      myServo.write(180);
    }

    // Turn the LED on to show a signal was received
    digitalWrite(LED_PIN, HIGH);
    // Keep it on for 100 ms so the blink is easy to see
    delay(100);
    // Turn the LED off
    digitalWrite(LED_PIN, LOW);

    // Tell the IR library to get ready for the next button press
    IrReceiver.resume();
  }
}
