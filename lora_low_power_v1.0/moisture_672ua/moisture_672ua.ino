// LoRa 9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example LoRa9x_RX

//Function:Transmit DHT11 to Lora
//Author: Charlin
//Date:2019/12/11

#include <SPI.h>
#include "RH_RF95.h"
#include <avr/wdt.h>
#include <avr/sleep.h>
#include "I2C_AHT10.h"
#include <Wire.h>

#define NODENAME "LORA_POWER_1"

#define RFM95_CS 10
#define RFM95_RST 4
#define RFM95_INT 2
#define RF95_FREQ 433.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
AHT10 humiditySensor;

int sensorPin = A2; // select the input pin for the potentiometer
int sensorPowerCtrlPin = 5;
int sensorValue = 0; // variable to store the value coming from the sensor

int shu = 0;

int16_t packetnum = 0;   // packet counter, we increment per xmission
float temperature = 0.0; //
float humidity = 0.0;

void setup()
{
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  //while (!Serial);
  Serial.begin(115200);
  Serial.println("Soil start.");
  delay(100);

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init())
  {
    Serial.println("LoRa radio init failed");
    while (1)
      ;
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ))
  {
    Serial.println("setFrequency failed");
    while (1)
      ;
  }
  Serial.print("Set Freq to: ");
  Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  rf95.sleep(); //休眠SX1278

  //AHT10
  pinMode(sensorPowerCtrlPin, OUTPUT);
  digitalWrite(sensorPowerCtrlPin, HIGH); //Sensor power on

  Wire.begin();
  if (humiditySensor.begin() == false)
  {
    Serial.println("AHT10 not detected. Please check wiring. Freezing.");
  }
  else
    Serial.println("AHT10 acknowledged.");

  read_sensor();
  //setup over

  low_power_set();
}

void loop()
{
  wdt_disable();

  if (shu > 450) //(7+1) x 8S
  {
    //code start
    Serial.println("Code start*************************************");

    read_sensor();
    all_pins_low();
    //code end
    Serial.println("Code end*************************************");

    //count init
    shu = 0;
  }

  watchdog_init();
  delay(10);
  sleep_cpu();
}

ISR(WDT_vect)
{
  Serial.print("[Watch dog]");
  Serial.println(shu);
  delay(100);
  shu++;
  wdt_reset();
}

//Set low power mode and into sleep
void low_power_set()
{
  Serial.println("[Set]Sleep Mode Set");
  all_pins_low();
  delay(10);
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();
  watchdog_init();
  delay(10);
  sleep_cpu();
}

//Enable watch dog
void watchdog_init()
{
  MCUSR &= ~(1 << WDRF);
  WDTCSR |= (1 << WDCE) | (1 << WDE);

  //WDTCSR = 1 << WDP1 | 1 << WDP2; //1S
  WDTCSR = 1 << WDP0 | 1 << WDP3; //8S

  WDTCSR |= _BV(WDIE); //not rst, inter interrutp
  wdt_reset();
}

void read_sensor()
{
  digitalWrite(sensorPowerCtrlPin, HIGH); //Sensor power on
  for (int i = 0; i < 3; i++)
  {
    sensorValue = analogRead(sensorPin);
    delay(200);
    if (humiditySensor.available() == true)
    {
      temperature = humiditySensor.getTemperature();
      humidity = humiditySensor.getHumidity();
    }
    if (isnan(humidity) || isnan(temperature))
    {
      Serial.println(F("Failed to read from AHT sensor!"));
    }
  }
  digitalWrite(sensorPowerCtrlPin, LOW); //Sensor power on

  String message = "#" + (String)packetnum + " NAME:" + (String)NODENAME + " H:" + (String)humidity + " T:" + (String)temperature + " ADC:" + (String)sensorValue;
  Serial.println(message);

  // Send a message to rf95_server

  uint8_t radioPacket[message.length() + 1];
  message.toCharArray(radioPacket, message.length() + 1);

  radioPacket[message.length() + 1] = '\0';

  Serial.println("Sending...");
  delay(10);
  rf95.send((uint8_t *)radioPacket, message.length() + 1);
  Serial.println("Waiting for packet to complete...");
  packetnum++;
  delay(10);
  rf95.sleep(); //休眠SX1278
}

void all_pins_low()
{
  //0.672ma
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  delay(50);
}