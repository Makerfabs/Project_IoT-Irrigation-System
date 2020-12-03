# main.py
import network
import webrepl
import time

AUTH_OPEN = 0
AUTH_WEP = 1
AUTH_WPA_PSK = 2
AUTH_WPA2_PSK = 3
AUTH_WPA_WPA2_PSK = 4

SSID = "Makerfabs"
PASSWORD = "20160704"

def do_connect(ssid,psw):
    import network
    import time
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    #ap.config(essid='MKF-AP',authmode=AUTH_WPA_WPA2_PSK,password='12345678')
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    s = wlan.config("mac")
    mac = ('%02x:%02x:%02x:%02x:%02x:%02x').upper() %(s[0],s[1],s[2],s[3],s[4],s[5])
    print("Local MAC:"+mac) #鑾峰彇mac鍦板潃
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
        print('network config:', wlan.ifconfig())
    return wlan
	#import webrepl
	#webrepl.start()
	
def connect():
 do_connect(SSID,PASSWORD)
#do_connect()
