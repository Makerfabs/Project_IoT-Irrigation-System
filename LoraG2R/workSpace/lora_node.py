
from machine import Pin
import time
import config_lora
import random
import webserver
try:
  import usocket as socket
except:
  import socket
 
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
        self.sendMessage("Empty")
        onoff = "OFF"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)
        #设置accept阻塞时间
        s.settimeout(30)
        
        while True:
            #Relay收发
            last_node_status = {"relay":"NULL", "soil1":"NULL", "soil2": "NULL", "soil0":"NULL", "update_time":"NULL"}

            temp_msg = "RELAY" + onoff
            self.sendMessage(temp_msg)
            self.lora.receive()
            self.lora_timeout()
            self.relay_status = str(self.buff)
            last_node_status["relay"] = self.relay_status
            if last_node_status["relay"] == "":
                last_node_status["relay"] = "NULL"

            for i in range(3):
                soil_index = 'soil'+str(i)
                self.sendMessage(soil_index)
                self.lora.receive()
                self.lora_timeout()
                last_node_status[soil_index] = str(self.buff)
                if last_node_status[soil_index] == "":
                    last_node_status[soil_index] = "NULL"

            del self.node_list.list[0]
            self.node_list.list.append(last_node_status)

            self.show_all_status(self.node_list)         
            
            #阻塞lora，等待webserver请求
            self.sendMessage("Empty")
            print("Prepare accept")
            try:
                conn, addr = s.accept()
                print('Got a connection from %s' % str(addr))
                request = conn.recv(1024)
                request = str(request)
                print('Content = %s' % request)

                #解析请求并发送控制继电器指令
                led_on = request.find('/?led=on')
                led_off = request.find('/?led=off')
                if led_on == 6:
                    print('LED ON')
                    onoff = 'ON'
                if led_off == 6:
                    print('LED OFF')
                    onoff = 'OFF'
                response = webserver.web_page(self.relay_status)
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()
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
            if config_lora.millisecond() - now > 5000:
                print("Callback time out.")
                break
        self.flag = 0

    def show_all_status(self,node_List):
        self.lora.show_text(self.ip)
        self.lora.show_text('relay:'+ node_List.list[9]['relay'],0,10,clear_first = False)
        self.lora.show_text('soil0:'+ node_List.list[9]['soil0'],0,20,clear_first = False)
        self.lora.show_text('soil1:'+ node_List.list[9]['soil1'],0,30,clear_first = False)
        self.lora.show_text('soil2:'+ node_List.list[9]['soil2'],0,40,clear_first = False)
        self.lora.show_text(node_List.list[9]['update_time'],0,50,clear_first = False, show_now = True, hold_seconds = 1)

class Lora_Node_List:
    def __init__(self):
        self.list = []
        for i in range(10):
            self.list.append({"relay":"UNKNOW", "soil0":"1", "soil1": "2", "soil2":"3", "update_time":"16:32:00"})

