
#include <SPI.h>
#include <ArduinoJson.h>
#include "RH_RF95.h"

#define RFM95_CS 10
#define RFM95_RST 4
#define RFM95_INT 2
#define RF95_FREQ 433.0
#define RF95_PREMABLE_LENGTH 8

#define LORA_NODE_NAME "relay"
#define LORA_NODE_NUM "002"
#define LORA_NODE_TYPE 1 //0土壤传感器，1继电器,999test

#define LORA_RELAY_PIN 4
#define LORA_RELAY_STATUS_PIN 5
#define SENSOR_PIN A2 //土壤湿度传感器adc引脚
int sensorValue = 0;
int sensorPowerCtrlPin = 5;

//Lora芯片对象
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup()
{
  Serial.begin(115200);

  if (LORA_NODE_TYPE == 0)
    pinMode(sensorPowerCtrlPin, OUTPUT);

  if (LORA_NODE_TYPE == 1)
    pinMode(LORA_RELAY_PIN, OUTPUT);
  pinMode(LORA_RELAY_STATUS_PIN, OUTPUT);

  //重启
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  //初始化
  while (!rf95.init())
  {
    Serial.println("LoRa radio init failed");
    while (1)
      ;
  }
  Serial.println("LoRa radio init OK!");

  //设置频率
  if (!rf95.setFrequency(RF95_FREQ))
  {
    Serial.println("setFrequency failed");
    while (1)
      ;
  }
  Serial.print("Set Freq to: ");
  Serial.println(RF95_FREQ);

  //设置发射功率
  rf95.setTxPower(23, false);

  //设置前导码长度
  rf95.setPreambleLength(RF95_PREMABLE_LENGTH);
  Serial.print("Set setPreambleLength to: ");
  Serial.println(RF95_PREMABLE_LENGTH);

  //rf95.printRegisters();

  digitalWrite(sensorPowerCtrlPin, HIGH);
}

bool relay_state = false;
void loop()
{
  set_relay();
  // Now wait for a reply
  uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  //Serial.println("Waiting for reply...");
  delay(1000);
  if (rf95.available())
  {
    if (rf95.recv(buf, &len))
    {
      Serial.print("Got reply: ");
      String msg = String((char *)buf);
      Serial.println(msg);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);

      Serial.println();
      if (msg.indexOf("RELAY") == 0)
      {
        String message = "COMMAND WRONG";
        if (msg.indexOf("ON") != -1)
        {
          relay_state = true;
          message = "Already ON";
        }

        else if (msg.indexOf("OFF") != -1)
        {
          relay_state = false;
          message = "Already OFF";
        }

        Serial.println(message);

        delay(1000);
        // Send a message to rf95_server
        uint8_t radioPacket[message.length() + 1];
        message.toCharArray(radioPacket, message.length() + 1);
        radioPacket[message.length() + 1] = '\0';
        Serial.println("Sending...");
        delay(10);
        rf95.send((uint8_t *)radioPacket, message.length() + 1);

        delay(1000);
      }
    }
  }
}

void set_relay()
{
  if (relay_state)
  {
    digitalWrite(LORA_RELAY_PIN, HIGH);
    digitalWrite(LORA_RELAY_STATUS_PIN, LOW);
  }

  else
  {
    digitalWrite(LORA_RELAY_PIN, LOW);
    digitalWrite(LORA_RELAY_STATUS_PIN, HIGH);
  }
}