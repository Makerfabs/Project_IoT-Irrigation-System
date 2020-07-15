# Lora LOT Irrigation System

```c++
/*
Version:		V1.0
Author:			Vincent
Create Date:	2020/7/15
Note:
*/
```

![main]()

[toc]

# OVERVIEW

## Intruduce

[Makerfabs home page](https://www.makerfabs.com/)

[Makerfabs Wiki](https://makerfabs.com/wiki/index.php?title=Main_Page)

MakePython ...

![oversee]

## Equipment list

- [MakePython ESP32](https://www.makerfabs.com/wiki/index.php?title=MakePython_ESP32)

- soil
- relay



# DOWNLOAD CODE

## MicroPython Lora
- Plug the ESP32 and Lora extension boards together.

![connect_lora]()

- Connect MakePython ESP32 to your PC, open uPyCraft, and select connect to the serial port.

![connect_pc]

- Firmware will be prompted if it has not been burned before or for other reasons.Board selects ESP32, BURN_addr selects 0x1000, Erase_Flash selects Yes, com selects the port number.Firmware Choose Users, click Choose to Choose ESP32-IDF3-20190125-v1.10.bin in the folder.
- Download all python programs ending in.py from the \LoraS2G\workSpace to ESP32.
- Press the RST button on ESP32 to reset the development board.The screen will display the native IP after wifi connection

![show_lcd_1]()

- Enter ESP32's IP number in the browser: 192.168.1.123.Smartphones can do the same.

![open_web]()


## Burn Sensor
- Open arduino ide.
- Select Tools/Manage Libraries.
- Search ssd1306.
- Install Adafruit SSD1306 by Adafruit.
- If youer ardino ide version is old,maybe can't auto install dependent libraries. You may manual install or upgrade arduino ide, such as 1.8.13.
- Connect sensor to pc.
- Open file "/esp32_mp3/esp32_mp3.ino"
- Select Toos/board/Esp32 Dev Modue.
- Choice relay port.
- Push Upload.

![burn_sensor]()



## Burn Relay

- Open file "/esp32_mp3/esp32_mp3.ino"
- Connect relay to pc.
- Select Toos/board/Esp32 Dev Modue.
- Choice relay port.
- Push Upload.

![burn_relay]()

# CONTROL

## Web Control

- Enter the IP shown in the first row of the ESP32 LED screen in the browser address bar.
- 