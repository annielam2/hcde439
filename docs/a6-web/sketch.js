// A6 "Firefly Jar": steer a jar with the joystick to catch fireflies.
// Covering the photoresistor turns day into night (fireflies only come out in the dark).
// The real RGB LED glows in the mixed color of the fireflies in the jar.

// ---------- Settings ----------

// Serial speed; must match Serial.begin(9600) in the firmware
const BAUD_RATE = 9600;
// Joystick resting value: the pot's wiper sits at 2.5 V of 5 V, which reads 1023 * 2.5 / 5 = ~512
const JOY_CENTER = 512;
// Readings within this distance of center count as "not moving", so a slightly off-center stick doesn't drift
const JOY_DEADZONE = 60;
// Fastest the jar can move, in pixels per frame, when the stick is pushed all the way
const JAR_MAX_SPEED = 9;
// Light reading at or below this counts as full night (photoresistor covered); tune to your room
const NIGHT_READING = 200;
// Light reading at or above this counts as full day (normal room light); tune to your room
const DAY_READING = 500;
// Most fireflies flying free at full darkness
const MAX_FREE = 14;
// Most fireflies the jar can hold
const MAX_JAR = 8;
// Jar width in pixels
const JAR_W = 110;
// Jar height in pixels
const JAR_H = 140;
// How long (ms) the LED flashes white when you tap the glass with the mouse
const FLASH_MS = 150;
// Firefly colors: lime, amber, sky blue, pink (so the LED visibly mixes colors)
const FIREFLY_COLORS = [[170, 255, 60], [255, 190, 40], [70, 190, 255], [255, 80, 200]];

// ---------- State ----------

// The serial port object from p5.webserial
let port;
// The Connect/Disconnect button
let connectBtn;
// The p5 canvas (used to ignore clicks on the button)
let canvas;
// Latest joystick left/right reading from the Arduino
let joyX = JOY_CENTER;
// Latest joystick up/down reading from the Arduino
let joyY = JOY_CENTER;
// Latest light reading from the Arduino; start at "day"
let lightReading = DAY_READING;
// Whether the joystick button is pressed right now
let buttonDown = false;
// Whether the joystick button was pressed last time we checked (to detect a new press)
let buttonWasDown = false;
// How dark it is: 0 = day, 1 = full night
let darkness = 0;
// Jar's horizontal center position
let jarX;
// Jar's vertical center position
let jarY;
// Fireflies flying free in the sky
let freeFlies = [];
// Fireflies caught in the jar
let jarFlies = [];
// Time (ms) until which the LED should flash white
let flashUntil = 0;
// The last color message sent to the Arduino, so we only send when it changes
let lastSent = "";
// Star positions for the night sky
let stars = [];

// ---------- p5 setup and draw ----------

// setup() runs once when the page loads
function setup() {
  // Make a canvas that fills the browser window
  canvas = createCanvas(windowWidth, windowHeight);
  // Create the serial port and the connect button
  setupSerial();
  // Start the jar in the middle of the screen, horizontally
  jarX = width / 2;
  // Start the jar a bit below the vertical middle
  jarY = height * 0.6;
  // Make 80 stars
  for (let i = 0; i < 80; i++) {
    // Give each star a random position in the top 70% of the screen and a random twinkle offset
    stars.push({ x: random(width), y: random(height * 0.7), phase: random(TWO_PI) });
  }
  // Center text horizontally and vertically on its position
  textAlign(CENTER, CENTER);
}

// draw() runs about 60 times a second
function draw() {
  // If the Arduino is connected, read its latest sensor values
  if (checkPort()) readArduino();
  // Turn the light reading into darkness from 0 (day) to 1 (night)
  darkness = constrain(map(lightReading, DAY_READING, NIGHT_READING, 0, 1), 0, 1);
  // Move the jar with the joystick
  moveJar();
  // If the button just went from up to down, let the fireflies go
  if (buttonDown && !buttonWasDown) releaseFlies();
  // Remember the button state for next frame
  buttonWasDown = buttonDown;
  // Add or remove free fireflies to match how dark it is
  updateFlyCount();
  // Move free fireflies and catch any inside the jar
  updateFreeFlies();
  // Draw the sky, stars and ground
  drawScene();
  // Draw each free firefly
  for (let f of freeFlies) drawFly(f.x, f.y, f.col, f.phase, 1);
  // Draw the jar and the fireflies in it
  drawJar();
  // Draw the instructions and raw sensor readings
  drawHud();
  // Tell the Arduino what color the LED should be
  sendJarColor();
}

// ---------- Arduino -> Web ----------

// Read one line like "512,498,431,0" from the Arduino and store the values
function readArduino() {
  // Read everything up to the next newline (empty string if a full line hasn't arrived)
  let str = port.readUntil("\n");
  // Nothing new arrived this frame, so keep the old values
  if (str.length == 0) return;
  // Remove the newline/whitespace and split on commas into four pieces
  let arr = str.trim().split(",");
  // Ignore partial or garbled lines that don't have exactly four values
  if (arr.length != 4) return;
  // First value: joystick left/right (0-1023)
  joyX = Number(arr[0]);
  // Second value: joystick up/down (0-1023)
  joyY = Number(arr[1]);
  // Third value: light level (0-1023)
  lightReading = Number(arr[2]);
  // Fourth value: 1 means the button is pressed
  buttonDown = arr[3] == "1";
}

// Move the jar relative to its current position based on how far the stick is pushed
function moveJar() {
  // How far the stick is from center horizontally (about -512 to +511)
  let dx = joyX - JOY_CENTER;
  // How far the stick is from center vertically
  let dy = joyY - JOY_CENTER;
  // Inside the dead zone, treat horizontal as zero
  if (abs(dx) < JOY_DEADZONE) dx = 0;
  // Inside the dead zone, treat vertical as zero
  if (abs(dy) < JOY_DEADZONE) dy = 0;
  // Turn horizontal stick distance into a speed and move the jar
  jarX += map(dx, -512, 512, -JAR_MAX_SPEED, JAR_MAX_SPEED);
  // Turn vertical stick distance into a speed and move the jar
  jarY += map(dy, -512, 512, -JAR_MAX_SPEED, JAR_MAX_SPEED);
  // Keep the jar fully on screen left to right
  jarX = constrain(jarX, JAR_W / 2, width - JAR_W / 2);
  // Keep the jar fully on screen top to bottom
  jarY = constrain(jarY, JAR_H / 2, height - JAR_H / 2);
}

// ---------- Fireflies ----------

// Spawn or remove free fireflies so the count follows the darkness
function updateFlyCount() {
  // Target number of free fireflies: none in daylight, MAX_FREE at full night
  let target = floor(darkness * MAX_FREE);
  // If there are too few, sometimes add one (random so they trickle in, not all at once)
  if (freeFlies.length < target && random() < 0.05) freeFlies.push(makeFly(random(width), random(height * 0.75)));
  // If there are too many (it got lighter), sometimes one flies away
  if (freeFlies.length > target && random() < 0.05) freeFlies.shift();
}

// Create a firefly object at (x, y) with a random direction and color
function makeFly(x, y) {
  // Return position, velocity, color and a random glow offset so they don't blink in sync
  return { x: x, y: y, vx: random(-1, 1), vy: random(-1, 1), col: random(FIREFLY_COLORS), phase: random(TWO_PI) };
}

// Move each free firefly and check whether the jar caught it
function updateFreeFlies() {
  // Loop backwards so removing a caught firefly doesn't skip the next one
  for (let i = freeFlies.length - 1; i >= 0; i--) {
    // The firefly being updated
    let f = freeFlies[i];
    // Nudge its horizontal speed randomly so it wanders
    f.vx = constrain(f.vx + random(-0.15, 0.15), -1.6, 1.6);
    // Nudge its vertical speed randomly so it wanders
    f.vy = constrain(f.vy + random(-0.15, 0.15), -1.6, 1.6);
    // Move horizontally
    f.x += f.vx;
    // Move vertically
    f.y += f.vy;
    // Bounce off the left or right edge
    if (f.x < 0 || f.x > width) f.vx *= -1;
    // Bounce off the top edge or the grass
    if (f.y < 0 || f.y > height * 0.85) f.vy *= -1;
    // Is the firefly inside the jar horizontally?
    let insideX = abs(f.x - jarX) < JAR_W / 2;
    // Is the firefly inside the jar vertically?
    let insideY = abs(f.y - jarY) < JAR_H / 2;
    // If it's inside and the jar has room, catch it
    if (insideX && insideY && jarFlies.length < MAX_JAR) {
      // Add it to the jar at a random spot inside, keeping its color
      jarFlies.push({ rx: random(-JAR_W / 2 + 15, JAR_W / 2 - 15), ry: random(-JAR_H / 2 + 30, JAR_H / 2 - 15), col: f.col, phase: f.phase });
      // Remove it from the sky
      freeFlies.splice(i, 1);
    }
  }
}

// Open the jar: every caught firefly flies back into the sky
function releaseFlies() {
  // Go through each firefly in the jar
  for (let j of jarFlies) {
    // Make a free firefly at its on-screen spot (above the jar so it isn't instantly re-caught)
    let f = makeFly(jarX + j.rx, jarY - JAR_H / 2 - 20);
    // Keep its color
    f.col = j.col;
    // Send it upward
    f.vy = -1.6;
    // Put it back in the sky
    freeFlies.push(f);
  }
  // The jar is now empty, so the LED will go dark
  jarFlies = [];
}

// ---------- Web -> Arduino ----------

// Work out what color the LED should be right now, as [red, green, blue] from 0-255
function ledColor() {
  // While a tap-flash is happening, the LED is full white
  if (millis() < flashUntil) return [255, 255, 255];
  // An empty jar means the LED is off
  if (jarFlies.length == 0) return [0, 0, 0];
  // More fireflies = brighter jar: 1 firefly is 30% brightness, a full jar is 100%
  let level = map(jarFlies.length, 1, MAX_JAR, 0.3, 1);
  // Start with all three channels at zero
  let rgb = [0, 0, 0];
  // Do the same math for red (index 0), green (1) and blue (2)
  for (let c = 0; c < 3; c++) {
    // Add up this color channel across all caught fireflies
    let sum = 0;
    // Go through each caught firefly
    for (let j of jarFlies) sum += j.col[c];
    // Average the channel, scale by brightness level, and round to a whole number for analogWrite
    rgb[c] = round((sum / jarFlies.length) * level);
  }
  // Give back the mixed color
  return rgb;
}

// Send the LED color to the Arduino as text "r,g,b\n", but only when it changes
function sendJarColor() {
  // Can't send if the Arduino isn't connected
  if (!port.opened()) return;
  // Build the message, e.g. "255,200,40\n"
  let msg = ledColor().join(",") + "\n";
  // If the color is the same as last time, don't flood the serial line
  if (msg == lastSent) return;
  // Send the color to the Arduino
  port.write(msg);
  // Remember what we sent
  lastSent = msg;
}

// Mouse click = tap the glass: the real LED flashes white and the fireflies startle
function mousePressed(event) {
  // Ignore clicks that weren't on the canvas (like clicking the Connect button)
  if (event && event.target !== canvas.elt) return;
  // Flash the LED for FLASH_MS milliseconds starting now
  flashUntil = millis() + FLASH_MS;
}

// Keyboard: SPACE opens the jar and lets the fireflies go (same as the joystick button)
function keyPressed() {
  // Only respond to the space bar
  if (key === " ") releaseFlies();
}

// ---------- Drawing ----------

// Draw sky, stars and grass, all changing with the darkness
function drawScene() {
  // Blend the sky from daytime blue to night navy based on darkness
  background(lerpColor(color(135, 195, 235), color(10, 15, 40), darkness));
  // No outlines on stars
  noStroke();
  // Draw each star
  for (let s of stars) {
    // Stars fade in with darkness and twinkle slowly
    fill(255, 255, 255, darkness * (150 + 100 * sin(frameCount * 0.03 + s.phase)));
    // Draw the star as a small dot
    circle(s.x, s.y, 2);
  }
  // Grass color blends from green to dark green with darkness
  fill(lerpColor(color(90, 160, 70), color(15, 40, 25), darkness));
  // Draw the grass along the bottom 15% of the screen
  rect(0, height * 0.85, width, height * 0.15);
}

// Draw one glowing firefly at (x, y); scale makes jar flies glow a little bigger
function drawFly(x, y, col, phase, scale) {
  // Glow brightness pulses over time; the phase keeps fireflies out of sync
  let a = 140 + 115 * sin(frameCount * 0.08 + phase);
  // No outline
  noStroke();
  // Soft outer glow, mostly transparent
  fill(col[0], col[1], col[2], a * 0.3);
  // Draw the glow
  circle(x, y, 24 * scale);
  // Bright core
  fill(col[0], col[1], col[2], a);
  // Draw the core
  circle(x, y, 7 * scale);
}

// Draw the jar, its glow, and the fireflies inside
function drawJar() {
  // Draw rectangles from their center so the jar is centered on (jarX, jarY)
  rectMode(CENTER);
  // If the jar has fireflies, draw a soft glow behind it in the mixed LED color
  if (jarFlies.length > 0) {
    // No outline for the glow
    noStroke();
    // Use the same color as the real LED so the screen and the real world match
    let rgb = ledColor();
    // Glow color, transparent
    fill(rgb[0], rgb[1], rgb[2], 70);
    // Draw the glow a bit bigger than the jar
    ellipse(jarX, jarY, JAR_W * 1.8, JAR_H * 1.5);
  }
  // Glass is a faint transparent white
  fill(255, 255, 255, 40);
  // Glass outline is light blue-white
  stroke(220, 240, 255, 200);
  // Outline thickness
  strokeWeight(3);
  // Jar body with rounded corners
  rect(jarX, jarY, JAR_W, JAR_H, 18);
  // Lid color: brass
  fill(180, 140, 60);
  // No outline on the lid
  noStroke();
  // Draw the lid at the top of the jar
  rect(jarX, jarY - JAR_H / 2, JAR_W * 0.8, 14, 4);
  // Go back to the default corner-based rectangles for other drawing
  rectMode(CORNER);
  // Draw each caught firefly
  for (let j of jarFlies) {
    // Bounce it slightly inside the jar so it looks alive
    let wobbleX = 3 * sin(frameCount * 0.05 + j.phase);
    // Bob it slightly up and down
    let wobbleY = 3 * cos(frameCount * 0.04 + j.phase);
    // Draw it a bit bigger, startled (bigger still) while a tap flash is happening
    drawFly(jarX + j.rx + wobbleX, jarY + j.ry + wobbleY, j.col, j.phase, millis() < flashUntil ? 1.8 : 1.2);
  }
}

// Draw instructions, the jar count and the raw Arduino readings
function drawHud() {
  // No outline on text
  noStroke();
  // Text color: dark in the day, light at night
  fill(darkness > 0.5 ? 235 : 20);
  // Instruction text size
  textSize(16);
  // Instructions across the top
  text("Cover the light sensor to make it night | Joystick: move jar | Joystick button or SPACE: release | Click: tap the glass", width / 2, 70);
  // Bigger text for the count
  textSize(22);
  // How many fireflies are in the jar
  text("Fireflies in jar: " + jarFlies.length + " / " + MAX_JAR, width / 2, 100);
  // Small text for the readings
  textSize(12);
  // Raw readings, handy for calibrating NIGHT_READING / DAY_READING
  text("x " + joyX + "   y " + joyY + "   light " + lightReading + "   button " + (buttonDown ? 1 : 0) + "   LED " + ledColor().join(","), width / 2, height - 20);
}

// ---------- Serial helpers (based on the class p5-arduino examples) ----------

// Create the serial port, reconnect if possible, and make the connect button
function setupSerial() {
  // Create a p5.webserial port object
  port = createSerial();
  // Get ports this page has used before (the browser remembers permission)
  let usedPorts = usedSerialPorts();
  // If there is one, reopen it automatically at our baud rate
  if (usedPorts.length > 0) port.open(usedPorts[0], BAUD_RATE);
  // Make the button
  connectBtn = createButton("Connect to Arduino");
  // Put it in the top-left corner
  connectBtn.position(20, 20);
  // Run onConnectButtonClicked when it's clicked
  connectBtn.mouseClicked(onConnectButtonClicked);
}

// Update the button label and return whether the port is open
function checkPort() {
  // If the port isn't open...
  if (!port.opened()) {
    // ...offer to connect
    connectBtn.html("Connect to Arduino");
    // Report that it's closed
    return false;
  }
  // The port is open, so offer to disconnect
  connectBtn.html("Disconnect");
  // Report that it's open
  return true;
}

// Open or close the serial port when the button is clicked
function onConnectButtonClicked() {
  // Forget the last color sent, so the current color is re-sent after connecting
  lastSent = "";
  // If not connected, open the browser's port picker at our baud rate
  if (!port.opened()) port.open(BAUD_RATE);
  // Otherwise close the connection
  else port.close();
}

// Keep the canvas the size of the window if it's resized
function windowResized() {
  // Resize the canvas to the new window size
  resizeCanvas(windowWidth, windowHeight);
}
