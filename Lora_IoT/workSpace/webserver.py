#webserver.py
import network
import webrepl
import time
from machine import Pin
try:
  import usocket as socket
except:
  import socket

AUTH_OPEN = 0
AUTH_WEP = 1
AUTH_WPA_PSK = 2
AUTH_WPA2_PSK = 3
AUTH_WPA_WPA2_PSK = 4

SSID = "Makerfabs"      #Modify here with SSID
PASSWORD = "20160704"   #Modify here with PWD
led = Pin(5, Pin.OUT)
ip = "ip get wrong"

def web_page(msg):
  table_str = """<table border="1"><tr><th>update_time</th><th>relay</th><th style="color:green">soil0</th><th style="color:green">soil1</th><th style="color:green">soil2</th></tr>"""
  for i in range(10):
    table_str += "<tr><th>" + msg[i]['update_time'] + "</th><th>" + msg[i]['relay'] + """</th><th style="color:green">""" + msg[i]['soil0'] + """</th><th style="color:green">""" + msg[i]['soil1'] + """</th><th style="color:green">""" + msg[i]['soil2'] + "</th></tr>"
  table_str += """</table>"""

  html ="""
  <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="600"/></head>
    <body>
      <img src="https://makerfabs.com/image/cache/logo11-190x63.png" />
      <h1>Lora IoT Irrigation System</h1>
      <h2>Sensors status:</h2>
      """ + table_str + """
      <a href=\"?led=on\">
        <button style="background-color: #7ED321">RELAY ON</button>
      </a>
      <a href=\"?led=water\">
        <button style="background-color: #7ED321">WATER</button>
      </a>
      <a href=\"?led=off\">
        <button style="background-color: #FFFFFF">RELAY OFF</button>
      </a>
      <a href=\"?led=donothing\">
        <button style="background-color: #FFFFFF">Fresh</button>
      </a>
    </body>
  </html>
  """
  return html

def do_connect(ssid,psw):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    s = wlan.config("mac")
    mac = ('%02x:%02x:%02x:%02x:%02x:%02x').upper() %(s[0],s[1],s[2],s[3],s[4],s[5])
    print("Local MAC:"+mac) #get mac 
    wlan.connect(ssid, psw)
    if not wlan.isconnected():
        print('connecting to network...' + ssid)
        wlan.connect(ssid, psw)

    start = time.ticks_ms() # get millisecond counter
    while not wlan.isconnected():
        time.sleep(1) # sleep for 1 second
        if time.ticks_ms()-start > 20000:
            print("connect timeout!")
            break

    if wlan.isconnected():
        print('network config:', wlan.ifconfig()[0])
        global ip
        ip = str(wlan.ifconfig()[0])
    return wlan

def connect():
 do_connect(SSID,PASSWORD)
 global ip
 return ip





