
#MakePython ESP32 对象文件 有OLED版本
#包含esp32,Lora模块，SSD1306的引脚定义
import controller_esp
import display_ssd1306_i2c
 

class Controller(controller_esp.Controller, display_ssd1306_i2c.Display):

    # LoRa config
    PIN_ID_FOR_LORA_RESET = 33
    
    PIN_ID_FOR_LORA_SS = 32
    PIN_ID_SCK = 14
    PIN_ID_MOSI = 13
    PIN_ID_MISO = 12
    
    PIN_ID_FOR_LORA_DIO0 = 36
    PIN_ID_FOR_LORA_DIO1 = None 
    PIN_ID_FOR_LORA_DIO2 = None 
    PIN_ID_FOR_LORA_DIO3 = None
    PIN_ID_FOR_LORA_DIO4 = None
    PIN_ID_FOR_LORA_DIO5 = None 
    
    
    # OLED config
    PIN_ID_FOR_OLED_RESET = 16
    PIN_ID_SDA = 4
    PIN_ID_SCL = 5
    OLED_I2C_ADDR = 0x3C    
    OLED_I2C_FREQ = 100000
    OLED_WIDTH = 128
    OLED_HEIGHT = 64
    
    
    # ESP config
    ON_BOARD_LED_PIN_NO = 17
    ON_BOARD_LED_HIGH_IS_ON = False
    GPIO_PINS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                 12, 13, 14, 15, 16, 17, 18, 19, 21, 22,
                 23, 25, 26, 27, 32, 34, 35, 36, 37, 38, 39) 
                 
    #构造函数
    def __init__(self, 
                 pin_id_led = ON_BOARD_LED_PIN_NO, 
                 on_board_led_high_is_on = ON_BOARD_LED_HIGH_IS_ON,
                 pin_id_reset = PIN_ID_FOR_LORA_RESET,
                 blink_on_start = (2, 0.5, 0.5),
                 oled_width = OLED_WIDTH, oled_height = OLED_HEIGHT, 
                 scl_pin_id = PIN_ID_SCL, sda_pin_id = PIN_ID_SDA, 
                 freq = OLED_I2C_FREQ):

        #复用构造函数         
        controller_esp.Controller.__init__(self,
                                           pin_id_led,
                                           on_board_led_high_is_on,
                                           pin_id_reset,
                                           blink_on_start)
                                           
        self.reset_pin(self.prepare_pin(self.PIN_ID_FOR_OLED_RESET))        
        display_ssd1306_i2c.Display.__init__(self, 
                                             width = oled_width, height = oled_height, 
                                             scl_pin_id = scl_pin_id, sda_pin_id = sda_pin_id, 
                                             freq = freq)                                             
        self.show_text('Hello Makerfabs!',0,0,clear_first = False)
        self.show_text('Life is short!',0,16,clear_first = False)
        self.show_text('You need python!',0,32,clear_first = False)
        self.show_text('Makepython ESP32!',0,48,clear_first = False, show_now = True, hold_seconds = 1)
                         


    def add_transceiver(self, 
                        transceiver, 
                        pin_id_ss = PIN_ID_FOR_LORA_SS,
                        pin_id_RxDone = PIN_ID_FOR_LORA_DIO0,
                        pin_id_RxTimeout = PIN_ID_FOR_LORA_DIO1,
                        pin_id_ValidHeader = PIN_ID_FOR_LORA_DIO2,
                        pin_id_CadDone = PIN_ID_FOR_LORA_DIO3,     
                        pin_id_CadDetected = PIN_ID_FOR_LORA_DIO4,
                        pin_id_PayloadCrcError = PIN_ID_FOR_LORA_DIO5):
         
        transceiver.show_text = self.show_text
        transceiver.show_packet = self.show_packet
        transceiver.show_text_wrap = self.show_text_wrap
        transceiver.clear = self.clear
        transceiver.fill_rect = self.fill_rect
        
        return super().add_transceiver(transceiver, 
                                       pin_id_ss,
                                       pin_id_RxDone,
                                       pin_id_RxTimeout,
                                       pin_id_ValidHeader,
                                       pin_id_CadDone,
                                       pin_id_CadDetected,
                                       pin_id_PayloadCrcError) 
                                       
                                       
    def show_packet(self, payload_string, rssi = None):
        self.clear()
        line_idx = 0
        if rssi:
            self.show_text('RSSI: {}'.format(rssi), x = 0, y = line_idx * 10, clear_first = False, show_now = False)
            line_idx += 1        
        self.show_text_wrap(payload_string, start_line = line_idx, clear_first = False)



