#include <Wiegand.h>
#include "Adafruit_Keypad.h"

// These are the pins connected to the Wiegand D0 and D1 signals.
// Ensure your board supports external Interruptions on these pins
#define PIN_D0 12
#define PIN_D1 13
#define KEYPAD_PID3845
// define your pins here
// can ignore ones that don't apply
#define R1    5
#define R2    6
#define R3    10
#define R4    11
#define C1    A1
#define C2    A2
#define C3    A3
#include "keypad_config.h"
// The object that handles the wiegand protocol
Wiegand wiegand;
Adafruit_Keypad customKeypad = Adafruit_Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS);
char PIN[10];
int semafoo = 0;
int keyPadTimeOut = 0;
// Initialize Wiegand reader
void setup() {
  Serial.begin(9600);
  customKeypad.begin();
  //Install listeners and initialize Wiegand reader
  wiegand.onReceive(receivedData, "Card readed: ");
  wiegand.onReceiveError(receivedDataError, "Error with message verification");
  wiegand.onStateChange(stateChanged, "State changed: ");
  wiegand.begin(Wiegand::LENGTH_ANY, true);

  //initialize pins as INPUT and attaches interruptions
  pinMode(PIN_D0, INPUT);
  pinMode(PIN_D1, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_D0), pinStateChanged, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_D1), pinStateChanged, CHANGE);

  //Sends the initial pin state to the Wiegand library
  pinStateChanged();
}

// Every few milliseconds, check for pending messages on the wiegand reader
// This executes with interruptions disabled, since the Wiegand library is not thread-safe
void loop() {
  customKeypad.tick(); //scan keypad
  semafoo++; //increment counter (flush only runs every 10th loop)
  keyPadTimeOut++;
  while(customKeypad.available()){
    keypadEvent e = customKeypad.read();
    if(e.bit.EVENT == KEY_JUST_PRESSED) {
      keyPadTimeOut = 1;
      if((char)e.bit.KEY != '#') {
        for(int i = 0; i < 10; i++) {
          if(PIN[i] == 0x00) {
            PIN[i] = (char)e.bit.KEY;
            break;
          }
        }
       } else {
        Serial.print("PIN: ");
        Serial.println(PIN);
        for(int i = 0; i < 10; i++) {
          PIN[i] = 0x00;
        }
      }
    }
  }
  //wiegand flush (not really sure what it does but wiegand library runs it every 100ms)
  if(semafoo % 10 == 0) {
    noInterrupts();
    wiegand.flush();
    interrupts();
  } if(keyPadTimeOut % 400 == 0) {
    //Every 4 seconds w/o button press clear keypad
    for(int i = 0; i < 10; i++) {
      PIN[i] = 0x00;
    }
  }
  delay(10);
}

// When any of the pins have changed, update the state of the wiegand library
void pinStateChanged() {
  wiegand.setPin0State(digitalRead(PIN_D0));
  wiegand.setPin1State(digitalRead(PIN_D1));
}

// Notifies when a reader has been connected or disconnected.
// Instead of a message, the seconds parameter can be anything you want -- Whatever you specify on `wiegand.onStateChange()`
void stateChanged(bool plugged, const char* message) {
    Serial.print(message);
    Serial.println(plugged ? "CONNECTED" : "DISCONNECTED");
}

// Notifies when a card was read.
// Instead of a message, the seconds parameter can be anything you want -- Whatever you specify on `wiegand.onReceive()`
void receivedData(uint8_t* data, uint8_t bits, const char* message) {
    Serial.print(message);
    Serial.print(bits);
    Serial.print("bits / ");
    //Print value in HEX
    uint8_t bytes = (bits+7)/8;
    for (int i=0; i<bytes; i++) {
        Serial.print(data[i] >> 4, 16);
        Serial.print(data[i] & 0xF, 16);
    }
    Serial.println();
}

// Notifies when an invalid transmission is detected
void receivedDataError(Wiegand::DataError error, uint8_t* rawData, uint8_t rawBits, const char* message) {
    Serial.print(message);
    Serial.print(Wiegand::DataErrorStr(error));
    Serial.print(" - Raw data: ");
    Serial.print(rawBits);
    Serial.print("bits / ");

    //Print value in HEX
    uint8_t bytes = (rawBits+7)/8;
    for (int i=0; i<bytes; i++) {
        Serial.print(rawData[i] >> 4, 16);
        Serial.print(rawData[i] & 0xF, 16);
    }
    Serial.println();
}
