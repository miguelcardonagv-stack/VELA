from smbus2 import SMBus
import time

class lcd:
    def __init__(self, addr=0x27, port=1):
        self.bus = SMBus(port)
        self.addr = addr
        # Inicialización de pantalla
        for cmd in [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]:
            self.write(cmd, 0)
        
    def write(self, cmd, mode):
        b1 = mode | (cmd & 0xF0) | 0x08
        b2 = mode | ((cmd << 4) & 0xF0) | 0x08
        for b in [b1, b1 | 0x04, b1, b2, b2 | 0x04, b2]:
            try: self.bus.write_byte(self.addr, b)
            except: pass
            
    def display(self, l1, l2):
        self.write(0x01, 0)
        time.sleep(0.005)
        for i, row in enumerate([l1, l2]):
            self.write(0x80 + (0x40 * i), 0)
            for char in row[:16]:
                self.write(ord(char), 1)
