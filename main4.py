# Brian Lesko 12/2023

import pyb 
import network
import socket
import time

class portenta:

    def __init__(self):
        self.log = []
        self.wlan = network.WLAN(network.STA_IF) # Connect to wifi 
        self.my_serial = pyb.USB_VCP() # Connect to serial port
        self.LEDS = self.initLEDS(brightness=10)
        # Networking
        self.IP = None
        self.client_socket = False
        self.client_address = None 
        self.server = None

    def initLEDS(self,brightness=22):
        redLED = pyb.LED(1)
        redLED.intensity(22)
        greenLED = pyb.LED(2)
        greenLED.intensity(22)
        blueLED = pyb.LED(3)
        blueLED.intensity(2)
        return [redLED, greenLED, blueLED]
    
    def flashWhite(self):
        for i in range(3):
            for led in self.LEDS: led.on()
            pyb.delay(50)
            for led in self.LEDS: led.off()
            pyb.delay(50)

    def flashPurple(self):
        for i in range(3):
            self.LEDS[0].on()
            self.LEDS[2].on()
            pyb.delay(50)
            self.LEDS[0].off()
            self.LEDS[2].off()
            pyb.delay(50)

    def flashLED(self,color,num=1):
        for i in range(1):
            for led in self.LEDS: led.off()
            self.LEDS[color].on()
            pyb.delay(50)
            self.LEDS[color].off()
            pyb.delay(50)

    def do_connect(self):
        if self.wlan.isconnected() == False:
            self.flashLED(2)
            self.log_and_serial_send("Attempting to connect to wifi")
            self.wlan.active(True)
            if not self.wlan.isconnected():
                SSID = 'Lesko'
                self.wlan.connect(SSID, '12081999')
                start_time = time.time()  # Record the start time
                timeout = 5  # Set the timeout duration in seconds
                while not self.wlan.isconnected():
                    self.flashLED(2)
                    if time.time() - start_time > timeout:
                        self.flashLED(0,5)
                        break
            if self.wlan.isconnected():
                self.log_and_serial_send(f'Successfully connected to {SSID}')
            else:
                self.log_and_serial_send('Failed to connect within the timeout period')
            return self.wlan
        if self.wlan.isconnected() == True:
            self.IP = str(self.wlan.ifconfig()[0])
            self.flashLED(2)
            self.flashLED(1)
            self.flashLED(2)

    def accept_client(self):
        if self.wlan.isconnected() == False or self.IP is None:
            return 0
        if self.client_socket is not None and self.client_address is not None:
            self.log_and_serial_send(f'Still Connected to {self.client_address}')
            return 1
        if self.wlan.isconnected() == True:
            self.log_and_serial_send('Accepting a new client socket')
            if self.server is None:
                self.log_and_serial_send('Creating a new Server Socket')
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((self.IP, 12345))  # Set the server's IP address
                self.log_and_serial_send(f'Server Socket Created at {self.IP}')
                self.server.listen() # makes the server a "listening socket"
            try:
                self.log_and_serial_send(f'About to wait for connections')
                self.LEDS[2].on()
                conn, addr = self.server.accept()
                self.log_and_serial_send(f"Connected to client at {addr}")
                self.client_socket = conn
                self.client_address = addr
                return 1
            except:
                self.log_and_serial_send("Failed to connect to client")
                return 0
        
    def serial_send(self, message):
        if self.my_serial.isconnected() == False:
            return 0 
        if self.my_serial.isconnected() == True:
            message = message + '\n'
            if isinstance(message, list):
                message = '\n'.join(message)
            self.my_serial.write(message.encode())
            return 1
        
    def serial_read(self):
        if self.my_serial.isconnected() == False:
            return 0 
        if self.my_serial.isconnected() == True:
            self.flashLED(1)
            bytes = self.my_serial.readline()
            if bytes is not None: 
                message = bytes.decode('utf-8')
                self.log_and_serial_send(f'Received over Serial: {message}')
                return message
            return 0
        
    def log_and_serial_send(self, message):
        self.log.append(message)
        self.serial_send(message)
        
    def TCP_read(self):
        if self.client_address is None:
            return 0
        if self.client_address is not None:
            self.flashLED(1)
            self.log_and_serial_send(f'Waiting to receive over TCP')
            bytes = self.client_socket.recv(1024)
            if bytes is not None: 
                message = bytes.decode('utf-8')
                self.log_and_serial_send(f'Received over TCP: {message}')
                return message
            return 0
        
    def TCP_send(self, message):
        if self.client_address is None:
            return 0
        if self.client_address is not None:
            self.flashLED(1)
            self.log_and_serial_send(f'Sending over TCP')
            self.client_socket.send(message.encode())
            return 1


prt = portenta()

while True:
    prt.flashWhite()
    prt.do_connect()
    prt.accept_client()
    prt.serial_read()
    prt.TCP_read()
    # Do something with the received TCP data here
    prt.TCP_send("Hello from Portenta")

