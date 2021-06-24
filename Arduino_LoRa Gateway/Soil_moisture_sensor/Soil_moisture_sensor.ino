// LoRa 9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example LoRa9x_RX

//Function:Transmit Soil Moisture to Lora
//Author: Charlin
//Date:2020/06/12
//hardware: Lora Soil Moisture Sensor v1.1


#include <SPI.h>
#include <RadioLib.h>


#include "I2C_AHT10.h"
#include <Wire.h>
AHT10 humiditySensor;


int sensorPin = A2;    // select the input pin for the potentiometer
int sensorValue = 0;  // variable to store the value coming from the sensor
int sensorPowerCtrlPin = 5;

void sensorPowerOn(void)
{
  digitalWrite(sensorPowerCtrlPin, HIGH);//Sensor power on 
}
void sensorPowerOff(void)
{
  digitalWrite(sensorPowerCtrlPin, LOW);//Sensor power on 
}

#define DIO0 2
#define DIO1 6
//#define DIO2 7
//#define DIO5 8

#define LORA_RST 4
#define LORA_CS 10

#define SPI_MOSI 11
#define SPI_MISO 12
#define SPI_SCK 13

#define FREQUENCY 434.0
#define BANDWIDTH 125.0
#define SPREADING_FACTOR 9
#define CODING_RATE 7
#define OUTPUT_POWER 10
#define PREAMBLE_LEN 8
#define GAIN 0

// Singleton instance of the radio driver
SX1278 radio = new Module(LORA_CS, DIO0, LORA_RST, DIO1, SPI, SPISettings());

void setup() 
{

  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, LOW);
  delay(100);
  digitalWrite(LORA_RST, HIGH);

  pinMode(sensorPowerCtrlPin, OUTPUT);
  //digitalWrite(sensorPowerCtrlPin, LOW);//Sensor power on 
  sensorPowerOn();
  //pinMode(sensorPin, INPUT);
  
  //while (!Serial);
  Serial.begin(115200);
  delay(100);

  //SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
  SPI.begin();
  
  Wire.begin(); //Join I2C bus
  //Check if the AHT10 will acknowledge
  if (humiditySensor.begin() == false)
  {
    Serial.println("AHT10 not detected. Please check wiring. Freezing.");
    //while (1);
  }
  else
    Serial.println("AHT10 acknowledged.");
    
  Serial.println("Marduino LoRa TX Test!");

  // manual reset
  digitalWrite(LORA_RST, LOW);
  delay(10);
  digitalWrite(LORA_RST, HIGH);
  delay(10);

  int state = radio.begin(FREQUENCY, BANDWIDTH, SPREADING_FACTOR, CODING_RATE, SX127X_SYNC_WORD, OUTPUT_POWER, PREAMBLE_LEN, GAIN);
    //int state = radio.begin();
    if (state == ERR_NONE)
    {
        Serial.println(F("success!"));
    }
    else
    {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (true)
            ;
    }
  Serial.println("LoRa radio init OK!");

  //rf95.setModemConfig(Bw125Cr48Sf4096);

  //Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM


  //dht.begin();
}

int16_t packetnum = 0;  // packet counter, we increment per xmission
float temperature=0.0;//
float humidity=0.0;

void loop()
{

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  //float humidity = 6.18;//dht.readHumidity();
  // Read temperature as Celsius (the default)

  sensorPowerOn();//
  delay(100);
  sensorValue = analogRead(sensorPin);
  delay(200);

  if (humiditySensor.available() == true)
  {
    //Get the new temperature and humidity value
    temperature = humiditySensor.getTemperature();
    humidity = humiditySensor.getHumidity();

    //Print the results
    Serial.print("Temperature: ");
    Serial.print(temperature, 2);
    Serial.print(" C\t");
    Serial.print("Humidity: ");
    Serial.print(humidity, 2);
    Serial.println("% RH");

  }
    // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println(F("Failed to read from AHT sensor!"));
    //return;
  }
  
  delay(100);
  //sensorPowerOff();

  Serial.print(F("Moisture ADC : "));
  Serial.println(sensorValue);

  
  //Serial.print(F("Humidity: "));
  //Serial.print(humidity);
  //Serial.print(F("%  Temperature: "));
  //Serial.print(temperature);
  //Serial.println("Humidity is " + (String)humidity);
  //Serial.println("Temperature is " + (String)temperature);

  String message = "#"+(String)packetnum+" Humidity:"+(String)humidity+"% Temperature:"+(String)temperature+"C"+" ADC:"+(String)sensorValue+" SOIL2";
  Serial.println(message);
  packetnum++;
  Serial.println("Transmit: Sending to rf95_server");
  
  // Send a message to rf95_server

  int state = radio.transmit(message);
   if (state == ERR_NONE)
    {
        // the packet was successfully transmitted
        Serial.println(F(" success!"));

        // print measured data rate
        Serial.print(F("[SX1278] Datarate:\t"));
        Serial.print(radio.getDataRate());
        Serial.println(F(" bps"));
    }
    else if (state == ERR_PACKET_TOO_LONG)
    {
        // the supplied packet was longer than 256 bytes
        Serial.println(F("too long!"));
    }
    else if (state == ERR_TX_TIMEOUT)
    {
        // timeout occurred while transmitting packet
        Serial.println(F("timeout!"));
    }
    else
    {
        // some other error occurred
        Serial.print(F("failed, code "));
        Serial.println(state);
    }

  delay(1000);
}
