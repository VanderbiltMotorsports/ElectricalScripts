const int signalPin = 2; // 555 output connected here (must be interrupt-capable)
volatile unsigned long startTime = 0;
volatile unsigned long pulseDuration = 0;
volatile bool newPulse = false;

void setup() {
  Serial.begin(9600);
  pinMode(signalPin, INPUT);

  // Start watching for rising edge
  attachInterrupt(digitalPinToInterrupt(signalPin), risingEdge, RISING);
}

void loop() {
  if (newPulse) {
    noInterrupts();
    unsigned long duration = pulseDuration;
    newPulse = false;
    interrupts();

    Serial.print("Pulse width: ");
    Serial.print(duration);
    Serial.println(" us");
  }
}

// Triggered when the pulse goes HIGH
void risingEdge() {
  startTime = micros();
  attachInterrupt(digitalPinToInterrupt(signalPin), fallingEdge, FALLING);
}

// Triggered when the pulse goes LOW
void fallingEdge() {
  pulseDuration = micros() - startTime;
  newPulse = true;
  attachInterrupt(digitalPinToInterrupt(signalPin), risingEdge, RISING);
}