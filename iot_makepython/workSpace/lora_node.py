
from machine import Pin
import time
import config_lora
import random
import webserver
try:
  import usocket as socket
except:
  import socket
import ntptime

 
class Lora_Gate:

    def __init__(self, name, lora, ip):
        self.name = name
        self.lora = lora
        self.sensor_adc = "NULL"
        self.relay_status = "NULL"
        self.flag = 0
        self.buff = ""
        self.ip = ip
        self.node_list = Lora_Node_List()

    #模式配置
    def working(self):
        print(self.node_list.list)
        self.show_all_status(self.node_list)
        print("MODE_GATE")
        self.lora.onReceive(self.on_gate_receiver)
        self.lora.receive()
        self.gate_working()
        pass
    
    #发送数据
    def sendMessage(self, message):
        self.lora.println(message)
        print("Sending message:")
        print(message)


    #网关模式
    def gate_working(self):
        #获取时间
        try:
            ntptime.settime()
        except:
            self.lora.show_text_wrap('NTP time wrong , please reboot.')
        self.sendMessage("BEGIAN")
        onoff = "OFF"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)
        #设置accept阻塞时间
        s.settimeout(600)
        last_time = 0
        relay_common = 0

        while True:
            now_time = time.time()
            if now_time - last_time > 60 or relay_common == 1:
                last_time = now_time
                relay_common = 0

                tm = time.localtime()
                t_hour = (tm[3] + 8) % 24
                t_min = tm[4]
                t_sec = tm[5]
                time_str = str(t_hour) + ':' + str(t_min) + ':' + str(t_sec)
                print(time_str)

                #Relay收发
                self.sendMessage("PREPARE")
                time.sleep(5)

                last_node_status = {"Relay":"NULL", "Soil1":"NULL", "Soil2": "NULL", "Soil3":"NULL", "Update_time":"NULL"}
                last_node_status["Update_time"] = time_str

                temp_msg = "RELAY" + onoff
                onoff = ""
                self.sendMessage(temp_msg)
                self.lora.receive()
                self.lora_timeout()
                self.relay_status = self.buff
                self.buff = ""
                last_node_status["Relay"] = self.relay_status
                if last_node_status["Relay"] == "":
                    last_node_status["Relay"] = "NULL"

                for i in range(1,4):
                    soil_index = 'Soil'+str(i)
                    self.sendMessage(soil_index)
                    self.lora.receive()
                    self.lora_timeout()
                    last_node_status[soil_index] = self.buff
                    self.buff = ""
                    if last_node_status[soil_index] == "":
                        last_node_status[soil_index] = "NULL"

                del self.node_list.list[0]
                self.node_list.list.append(last_node_status)

                self.show_all_status(self.node_list)         

                #阻塞lora，等待webserver请求
                self.sendMessage("OVER")
                print("Prepare accept")

            while True :
                try:
                    conn, addr = s.accept()
                    print('Got a connection from %s' % str(addr))
                    request = conn.recv(1024)
                    request = str(request)
                    print('Content = %s' % request)
                    if request.find("favicon") != -1:
                        conn.close()
                        continue
                    if request is "":
                        conn.close()
                        continue

                    #解析请求并发送控制继电器指令
                    led_on = request.find('/?led=on')
                    led_off = request.find('/?led=off')
                    led_water = request.find('/?led=water')
                    if led_on == 6:
                        print('RELAY ON')
                        onoff = 'ON'
                        relay_common = 1
                    if led_off == 6:
                        print('RELAY OFF')
                        onoff = 'OFF'
                        relay_common = 1
                    if led_water == 6:
                        print('RELAY WATER')
                        onoff = 'WATER'
                        relay_common = 1
                    response = webserver.web_page(self.node_list.list)
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    conn.close()
                    break
                except Exception as e:
                    print(e)


    #网关模式回调
    def on_gate_receiver(self, payload):    
        print("On gate receive") 
        rssi = self.lora.packetRssi()
        
        try:
            #print payload可知报文前4字节和后一字节无意义
            if int(payload[0]) == 255:
                length=len(payload)-1   
                payload_string = str((payload[4:length]),'utf-8')
            else:
                payload_string = str(payload,'utf-8')        
            print("Received message:\n{}".format(payload_string))
            self.buff = payload_string
            self.flag = 1

        except Exception as e:
            print(e)
        print("with RSSI {}\n".format(rssi))

    #lora回调超时控制
    def lora_timeout(self):
        print("wait lora callback")
        now = config_lora.millisecond()
        while(self.flag == 0):
            if config_lora.millisecond() - now > 2000:
                print("Callback time out.")
                break
        self.flag = 0

    def show_all_status(self,node_List):
        self.lora.show_text(self.ip)

        soil0 = node_List.list[9]['Soil1']
        if soil0 == "AHT10ERR" :
            pass
        elif soil0 != "NULL" :
            soil0 = soil0[soil0.find('ADC'):]


        soil1 = node_List.list[9]['Soil2']
        if soil1 == "AHT10ERR" :
            pass
        elif soil1 != "NULL" :
            soil1 = soil1[soil1.find('ADC'):]


        soil2 = node_List.list[9]['Soil3']
        if soil2 == "AHT10ERR" :
            pass
        elif soil2 != "NULL" :
            soil2 = soil2[soil2.find('ADC'):]

        self.lora.show_text('Relay:'+ node_List.list[9]['Relay'],0,10,clear_first = False)
        self.lora.show_text('Soil1:'+ soil0,0,20,clear_first = False)
        self.lora.show_text('Soil2:'+ soil1,0,30,clear_first = False)
        self.lora.show_text('Soil3:'+ soil2,0,40,clear_first = False)
        self.lora.show_text(node_List.list[9]['Update_time'],0,50,clear_first = False, show_now = True, hold_seconds = 1)

class Lora_Node_List:
    def __init__(self):
        self.list = []
        for i in range(10):
            self.list.append({"Relay":"default", "Soil1":"default", "Soil2": "default", "Soil3":"default", "Update_time":"00:00:00"})

