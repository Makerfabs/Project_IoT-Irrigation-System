

import time
import config_lora


from connectWiFi import do_connect
import urequests
# https://thingspeak.com/channels/1035244
API_KEY = 'YOUR_API_KEY'

ssid = "Makerfabs"
pswd = "20160704"

wlan = do_connect(ssid, pswd)
s = wlan.config("mac")
wifimac = (
    'MAC:%02x-%02x-%02x-%02x-%02x-%02x ').upper() % (s[0], s[1], s[2], s[3], s[4], s[5])
print(wifimac)

if not wlan.isconnected():
    print('connecting to network...' + ssid)
    wlan.connect(ssid, psw)


msgCount = 0            # count of outgoing messages
INTERVAL = 2000         # interval between sends
INTERVAL_BASE = 2000    # interval between sends base


def duplexCallback(lora):
    print("LoRa Duplex with callback")
    lora.onReceive(on_receive)  # register the receive callback
    do_loop(lora)


def do_loop(lora):
    global msgCount

    lastSendTime = 0
    interval = 0

    while True:
        now = config_lora.millisecond()
        if now < lastSendTime:
            lastSendTime = now

        if (now - lastSendTime > interval):
            lastSendTime = now                                      # timestamp the message
            interval = (lastSendTime % INTERVAL) + \
                INTERVAL_BASE    # 2-3 seconds

            # message = "{} {}".format(config_lora.NODE_NAME, '#'+str(msgCount))
            message = "{} {}".format('Hello world ', '#'+str(msgCount))
            # send message
            sendMessage(lora, message)
            msgCount += 1

            lora.receive()                                          # go into receive mode


def sendMessage(lora, outgoing):
    lora.println(outgoing)
    # print("Sending message:\n{}\n".format(outgoing))


def on_receive(lora, payload):
    lora.blink_led()
    rssi = lora.packetRssi()
    try:

        length = len(payload)-1
        myStr = str((payload[4:length]), 'utf-8')
        print('%s\n' % (myStr))
        # #0 NAME:TEST1 H:47.16 T:31.36 ADC:845
        if myStr.find('LORA_POWER') == -1 :
            return

        length1 = myStr.find('#:')
        length2 = myStr.find('NAME:')
        length3 = myStr.find('H:')
        length4 = myStr.find('T:')
        length5 = myStr.find('ADC:')

        msg_index = myStr[(length1+len('#:')):(length2 - 1)]
        msg_name = myStr[length2+(len('NAME:')):(length3 - 1)]
        msg_h = myStr[(length3+len('H:')):(length4 - 1)]
        msg_t = myStr[(length4+len('T:')):length5 - 1]
        msg_adc = myStr[(length5+len('ADC:')):]

        print('Index:%s\n' % (msg_index))
        print('Name:%s\n' % (msg_name))
        print('Humidity:%s\n' % (msg_h))
        print('Temperature:%s\n' % (msg_t))
        print('ADC:%s\n' % (msg_adc))

        print("*** Received message ***\n{}".format(payload))
        if config_lora.IS_LORA_OLED:
            lora.show_packet(("{}".format(myStr)), rssi)

        if wlan.isconnected():
            global msgCount
            print('Sending to network...')
            # URL="https://api.thingspeak.com/update?api_key="+API_KEY+"&field5="+str(ADCValue)
            URL = "https://api.thingspeak.com/update?api_key="+API_KEY + \
                "&field1="+msg_name+"&field2="+msg_index+"&field3=" + \
                msg_h+"&field4="+msg_t+"&field5="+msg_adc
            res = urequests.get(URL)

            print(res.text)

    except Exception as e:
        print(e)
    print("with RSSI {}\n".format(rssi))
