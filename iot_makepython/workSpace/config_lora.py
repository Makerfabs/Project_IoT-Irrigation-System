#判断运行环境，mcu，是否有屏幕，加载相应配置。



import sys
import os 
import time

"""
>>>sys.implementation.name
'micropython'
>>> os.uname()
(sysname='esp32', nodename='esp32', release='1.9.1', version='v1.9.1-224-g83d3f3f-dirty on 2017-12-12', machine='ESP32 module with ESP32')
"""

#判断系统和单片机型号
IS_PC = False
IS_MICROPYTHON = (sys.implementation.name == 'micropython')
IS_ESP8266 = (os.uname().sysname == 'esp8266')
IS_ESP32 = (os.uname().sysname == 'esp32')
IS_LORA_OLED = None
IS_RPi = not (IS_MICROPYTHON or IS_PC)


def mac2eui(mac):
    mac = mac[0:6] + 'fffe' + mac[6:] 
    return hex(int(mac[0:2], 16) ^ 2)[2:] + mac[2:] 
    
#本测试为ESP32
if IS_MICROPYTHON:
            
    # Node Name
    import machine
    import ubinascii 

    """
    >>> machine.unique_id()
    b'$o(\xa6C\x90'
    >>> str(machine.unique_id(),"utf-8")
    '$o(C'
    >>> machine.unique_id().decode()
    '$o(C'
    >>> ubinascii.hexlify(machine.unique_id())
    b'246f28a64390'
    """

    #获取芯片的uuid
    uuid = ubinascii.hexlify(machine.unique_id()).decode()  
        
    if IS_ESP8266:
        NODE_NAME = 'ESP8266_'
    if IS_ESP32:
        NODE_NAME = 'ESP32_'
        import esp
        IS_LORA_OLED = True#(esp.flash_size() > 5000000)
        
    NODE_EUI = mac2eui(uuid)
    NODE_NAME = NODE_NAME + uuid

    print("NODE_NAME is :" , NODE_NAME)
    
    # millisecond
    millisecond = time.ticks_ms
    
    # Controller
    #判断是否为模拟SPI
    SOFT_SPI = None
    #判断是否是自带屏幕的版本
    if IS_LORA_OLED:
        #指向调用的Controller对象
        from controller_esp_lora_oled import Controller
        SOFT_SPI = False#True
    else:
        from controller_esp import Controller
    
    
        
if IS_RPi:
    
    # Node Name
    import socket
    NODE_NAME = 'RPi_' + socket.gethostname()
    
    # millisecond
    millisecond = lambda : time.time() * 1000
    
    # Controller
    from controller_rpi import Controller
    
    
    
if IS_PC:
        
    # Node Name
    import socket
    NODE_NAME = 'PC_' + socket.gethostname()
    
    # millisecond
    millisecond = lambda : time.time() * 1000
    
    # Controller
    from controller_pc import Controller  

