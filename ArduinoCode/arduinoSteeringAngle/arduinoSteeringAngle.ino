const int potPin = A0;
int potValue = 0;
float angle = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  potValue = analogRead(potPin);  // range: 0–1023
  angle = map(potValue, 0, 1023, -135, 135); // or whatever range your rotation supports

  Serial.print("Pot Value: ");
  Serial.print(potValue);
  Serial.print(" | Angle: ");
  Serial.println(angle);

  delay(50);
}
