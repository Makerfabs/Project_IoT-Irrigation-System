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
  table_str = """<tr><th>Update_time</th><th>Relay</th><th style="color:green">Soil1</th><th style="color:green">Soil2</th><th style="color:green">Soil3</th></tr>"""
  for i in range(10):
    table_str += "<tr><th>" + msg[i]['Update_time'] + "</th><th>" + msg[i]['Relay'] + """</th><th style="color:green">""" + msg[i]['Soil1'] + """</th><th style="color:green">""" + msg[i]['Soil2'] + """</th><th style="color:green">""" + msg[i]['Soil3'] + "</th></tr>"
  table_str += """</table>"""

  html ="""
<html>

<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="600" />
</head>

<body>
    <div id="content" style="text-align:center;background-color:#EEEEEE;height:150px;width:800px;float:center;">
        <img src="https://makerfabs.com/image/cache/logo11-190x63.png" />
        <h1>Lora IoT Irrigation System</h1>
    </div>
    <div id="menu" style="text-align:center;background-color:#FFD700;height:50px;width:800px;float:center;">
        <form method="get">
            <button name="led" type="submit" value="water">Water 10 Second</button>
            <button name="led" type="submit" value="off">Relay OFF</button>
            <button name="led" type="submit" value="donothing">Refresh Data</button>
        </form>
    </div>
    <table border="1" align="left" style="background-color: #00dbebcc;width:800;">
        <caption>Sensors status</caption>
""" + table_str + """
    </table>
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




"""
      <a href=\"?led=on\">
        <button style="background-color: #7ED321">RELAY ON</button>
      </a>
"""
