#include <RadioLib.h>

#define LORA_RELAY_PIN 4
#define LORA_RELAY_STATUS_PIN 5

#define NODENAME "RELAY"

#define DIO0 2
#define DIO1 6
#define DIO2 7
#define DIO5 8

#define LORA_RST 9
#define LORA_CS 10

#define SPI_MOSI 11
#define SPI_MISO 12
#define SPI_SCK 13

#define FREQUENCY 915.0
#define BANDWIDTH 125.0
#define SPREADING_FACTOR 9
#define CODING_RATE 7
#define OUTPUT_POWER 10
#define PREAMBLE_LEN 8
#define GAIN 0

SX1276 radio = new Module(LORA_CS, DIO0, LORA_RST, DIO1);

void setup()
{
    pinMode(LORA_RELAY_PIN, OUTPUT);
    pinMode(LORA_RELAY_STATUS_PIN, OUTPUT);

    Serial.begin(115200);

    // initialize SX1278 with default settings
    Serial.print(F("Initializing ... "));

    //int state = radio.begin();
    int state = radio.begin(FREQUENCY, BANDWIDTH, SPREADING_FACTOR, CODING_RATE, SX127X_SYNC_WORD, OUTPUT_POWER, PREAMBLE_LEN, GAIN);
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
    Serial.print(F("Waiting for incoming transmission ... "));
}

int relay_state = 0;

void loop()
{
    String str;
    int state = radio.receive(str);
    if (state == ERR_NONE)
    {
        // packet was successfully received
        Serial.println(F("success!"));

        // print the data of the packet
        Serial.print(F("[SX1278] Data:\t\t\t"));
        Serial.println(str);

        // print the RSSI (Received Signal Strength Indicator)
        // of the last received packet
        Serial.print(F("[SX1278] RSSI:\t\t\t"));
        Serial.print(radio.getRSSI());
        Serial.println(F(" dBm"));

        // print the SNR (Signal-to-Noise Ratio)
        // of the last received packet
        Serial.print(F("[SX1278] SNR:\t\t\t"));
        Serial.print(radio.getSNR());
        Serial.println(F(" dB"));

        // print frequency error
        // of the last received packet
        Serial.print(F("[SX1278] Frequency error:\t"));
        Serial.print(radio.getFrequencyError());
        Serial.println(F(" Hz"));
        if (str.startsWith(NODENAME))
        {
            String message = "???";
            switch (relay_state)
            {
            case 0:
                message = "OFF";
                break;
            case 1:
                message = "ON";
                break;
            default:
                message = "UNKNOW";
            }
            if (str.indexOf("ON") != -1)
            {
                relay_state = 1;
                message = "ON";
            }

            else if (str.indexOf("OFF") != -1)
            {
                relay_state = 0;
                message = "OFF";
            }
            else if (str.indexOf("WATER") != -1)
            {
                relay_state = 2;
                message = "WATER";
            }
            radio.transmit(message);
            set_relay();
        }
    }
}

void set_relay()
{
    if (relay_state == 2)
    {
        digitalWrite(LORA_RELAY_PIN, HIGH);
        digitalWrite(LORA_RELAY_STATUS_PIN, LOW);
        delay(10000);
        digitalWrite(LORA_RELAY_PIN, LOW);
        digitalWrite(LORA_RELAY_STATUS_PIN, HIGH);
        relay_state = 0;
    }
    else if (relay_state == 1)
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