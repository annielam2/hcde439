// Sources: the IRremote library by Armin Joachimsmeyer, Ken Shirriff et al. (https://github.com/Arduino-IRremote/Arduino-IRremote, MIT license);
// the IR receive code (IrReceiver.begin / decode / resume) follows that library's SimpleReceiver example.
// The MOSFET Gate wiring and analogWrite() dimming are adapted from our HCDE 439 L9 in-class mosfet_strip sketch,
// and the remote button codes come from my Assignment 4.

// Include the IRremote library (install "IRremote" v4.x in the Library Manager); it decodes the remote's button signals
#include <IRremote.hpp>

// Digital pin wired to the IR receiver's OUT pin (see schematic)
const int IR_PIN = 11;
// PWM-capable digital pin wired through R1 (220 ohm) to the MOSFET's Gate
const int GATE_PIN = 9;

// Code the remote sends for button 1 (found in Assignment 4 by printing IrReceiver.decodedIRData.command to the Serial Monitor)
const int BTN_1 = 0x0C;
// Code the remote sends for button 2 (found the same way)
const int BTN_2 = 0x18;
// Code the remote sends for button 3 (found the same way)
const int BTN_3 = 0x5E;

// analogWrite() level for "off": 0 out of 255 = 0% duty cycle, so the MOSFET never turns on and the strip is dark
const int LEVEL_OFF = 0;
// analogWrite() level for "dim": 90 out of 255 = about 35% duty cycle (why 90 is explained on the webpage)
const int LEVEL_LOW = 90;
// analogWrite() level for "full": 255 out of 255 = 100% duty cycle, so the MOSFET stays on and the strip is at full brightness
const int LEVEL_HIGH = 255;

// setup() runs once when the Arduino powers on or is reset
void setup() {
  // Start serial at 9600 baud so received button codes show in the Serial Monitor
  Serial.begin(9600);

  // Make the gate pin an output. On an Uno, pinMode(OUTPUT) does not by itself
  // force a voltage: the pin keeps whatever logic level it last had (LOW after
  // reset/power-up), and R2 (the 10k pulldown in the schematic) independently
  // holds the MOSFET's Gate near 0 V the whole time setup() is running, so the
  // strip stays off during this brief startup window no matter what.
  pinMode(GATE_PIN, OUTPUT);

  // Explicitly drive the gate pin LOW (0 V) so the MOSFET is OFF and the LED
  // strip is dark the instant setup() finishes, before loop() ever runs
  digitalWrite(GATE_PIN, LOW);

  // Start the IR receiver listening on IR_PIN
  IrReceiver.begin(IR_PIN);
}

// loop() runs over and over for as long as the board has power
void loop() {
  // Check whether the IR receiver has decoded a new button press
  if (IrReceiver.decode()) {
    // Read the numeric command code sent by whichever button was pressed
    int code = IrReceiver.decodedIRData.command;
    // Print the code in hex so it's easy to confirm which button was pressed
    Serial.println(code, HEX);

    // Button 1 pressed...
    if (code == BTN_1) {
      // ...turn the LED strip fully off by driving the MOSFET's gate to 0 V
      analogWrite(GATE_PIN, LEVEL_OFF);
      // Button 2 pressed...
    } else if (code == BTN_2) {
      // ...set the strip to a low, dim brightness
      analogWrite(GATE_PIN, LEVEL_LOW);
      // Button 3 pressed...
    } else if (code == BTN_3) {
      // ...set the strip to full brightness
      analogWrite(GATE_PIN, LEVEL_HIGH);
    }

    // Tell the IRremote library the code has been handled and it should listen for the next press
    IrReceiver.resume();
  }
}
