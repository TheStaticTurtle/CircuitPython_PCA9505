import time

def bitRead(value, bit):
    return (((value) >> (bit)) & 0x01)

def bitSet(value, bit):
    return value | (1 << (bit))

def bitClear(value, bit):
    return value & ~(1 << (bit))

def bitWrite(value, bit, bitvalue):
    return bitSet(value, bit) if bitvalue else bitClear(value, bit)

class PCA9505:
    OUTPUT               = 1
    INPUT                = 0
    HIGH                 = 1
    LOW                  = 0
    
    PORT0                = 0
    PORT1                = 1
    PORT2                = 2
    PORT3                = 3
    PORT4                = 4
    
    PCA9505_AI_ON        = 0x80
    PCA9505_AI_OFF       = 0x00

    PCA9505_BASE_ADDRESS = 0x20
    PCA9505_A0           = 0x01
    PCA9505_A1           = 0x02
    PCA9505_A2           = 0x04

    PCA9505_IP           = 0x00
    PCA9505_IP_PORTS     = [ 0x00,0x01,0x02,0x03,0x04 ]
    
    PCA9505_OP           = 0x08
    PCA9505_OP_PORTS     = [ 0x08,0x09,0x0A,0x0B,0x0C ]

    PCA9505_PI           = 0x10
    PCA9505_PI_PORTS     = [ 0x10,0x11,0x12,0x13,0x14 ]

    PCA9505_IOC          = 0x18
    PCA9505_IOC_PORTS    = [ 0x18,0x19,0x1A,0x1B,0x1C ]
    
    PCA9505_MSK          = 0x20
    PCA9505_IOC_PORTS    = [ 0x20,0x21,0x22,0x23,0x24 ]

    """docstring for PCA9505"""
    def __init__(self, i2c, address):
        super(PCA9505, self).__init__()
        self.i2c = i2c
        self.address = address
        self.io_interrupt = [0xff,0xff,0xff,0xff,0xff,]
        self.io_polarity = [0x00,0x00,0x00,0x00,0x00,]
        self.io_mode = [0x00,0x00,0x00,0x00,0x00,]
        
        if(not self._chip_present()):
            raise RuntimeError("Chip at address "+hex(address)+" is not present")
            
    def _lock_i2c(self):
        while not self.i2c.try_lock():
            pass

    def _unlock_i2c(self):
        self.i2c.unlock()
    
    def _chip_present(self):
        self._lock_i2c()
        is_present = self.address in i2c.scan()
        self._unlock_i2c()
        return is_present

    def _get_pin_port(self, pin):
        return pin // 8
    
    def _get_pin_bit(self, pin):
        return pin % 8
    
    def _send_port_data(self, reg, port, data):
        self._lock_i2c()
        i2c.writeto(self.address, bytes([ (reg + (port % 5)) | PCA9505.PCA9505_AI_OFF, data ]))
        self._unlock_i2c()
        
    def _get_port_data(self, reg, port):
        self._lock_i2c()
        i2c.writeto(self.address, bytes([ (reg + (port % 5)) | PCA9505.PCA9505_AI_OFF]))
        result = bytearray(1)
        i2c.readfrom_into(self.address, result)
        self._unlock_i2c()
        return result[0]
        
    def _send_io_data(self, reg, port):
        self._lock_i2c()
        i2c.writeto(self.address, bytes([reg | PCA9505.PCA9505_AI_ON, port[0], port[1], port[2], port[3], port[4] ]))
        self._unlock_i2c()

    def _get_io_data(self, reg):
        self._lock_i2c()
        i2c.writeto(self.address, bytes([ reg | PCA9505.PCA9505_AI_ON ]))
        result = bytearray(5)
        i2c.readfrom_into(self.address, result)
        data = [int(x) for x in result]
        self._unlock_i2c()
        return data
    
    def _set_io_interupt(self):
        self._send_io_data(PCA9505.PCA9505_MSK, self.io_interrupt)
        
    def _get_io_interupt(self):
        self.io_interrupt = self._get_io_data(PCA9505.PCA9505_MSK)
        return self.io_interrupt
    
    def _set_io_polarity(self):
        self._send_io_data(PCA9505.PCA9505_PI, self.io_polarity)
        
    def _get_io_polarity(self):
        self.io_polarity = self._get_io_data(PCA9505.PCA9505_PI)
        return self.io_polarity
    
    def _set_io_mode(self):
        self._send_io_data(PCA9505.PCA9505_IOC, [255-x for x in self.io_mode])
        
    def _get_io_mode(self):
        self.io_mode = [255-x for x in self._get_io_data(PCA9505.PCA9505_IOC)]
        return self.io_mode
    
    def begin(self):
        self.io_interrupt = [0xff,0xff,0xff,0xff,0xff,]
        self.io_polarity = [0x00,0x00,0x00,0x00,0x00,]
        self.io_mode = [0x00,0x00,0x00,0x00,0x00,]
        self._set_io_interupt()
        self._set_io_polarity()
        self._set_io_mode()
        
    def pinMode(self, pin, direction):
        pbit = self._get_pin_bit(pin)
        pport = self._get_pin_port(pin)
        data = self._get_port_data(PCA9505.PCA9505_IOC, pport);
        data = bitWrite(data, pbit, (0 if direction else 1));
        self._send_port_data(PCA9505.PCA9505_IOC, pport, data);
        
    def portMode(self, port, direction):
        self._send_port_data(PCA9505.PCA9505_IOC, port, 0x00 if direction else 0xFF);
        
    def pinWrite(self, pin, value):
        pbit = self._get_pin_bit(pin)
        pport = self._get_pin_port(pin)
        data = self._get_port_data(PCA9505.PCA9505_OP, pport);
        
        data = bitWrite(data, pbit, (1 if value else 0));
        self._send_port_data(PCA9505.PCA9505_OP, pport, data);
        
    def portWrite(self, port, value):
        self._send_port_data(PCA9505.PCA9505_OP, port, 0x00 if value else 0xFF);
    
    def pinRead(self, pin):
        return PCA9505.HIGH if (self._get_port_data(PCA9505.PCA9505_IP, self._get_pin_port(pin)) & (1 << self._get_pin_bit(pin))) else PCA9505.LOW;

    def portRead(self, port):
        return self._get_port_data(PCA9505.PCA9505_IP, port)
    
    def setPinInterrupt(self, pin, enable=True):
        pport = self._get_pin_port(pin)
        pbit = self._get_pin_bit(pin)
        data = self._get_port_data(PCA9505_MSK,pport);
        data = bitWrite(data, pbit, (0 if enable else 1));
        self._send_port_data(PCA9505_MSK, getPort(pin), data);
        
    def getPinInterrupt(self, pin):
        pport = self._get_pin_port(pin)
        pbit = self._get_pin_bit(pin)
        return (self._get_port_data(PCA9505_MSK, pport) >> pbit) & 0x01

    def setPortInterrupt(self, port, enable=True):
        self._send_port_data(PCA9505_MSK, PCA9505.PCA9505_MSK_PORTS[port], 0x00 if enable else 0xFF);

    def getPortInterrupt(self, port):
        return self._get_port_data(PCA9505_MSK, PCA9505.PCA9505_MSK_PORTS[port])
    
    def clearInterrupt(self):
        return self._get_port_data(PCA9505_MSK, PCA9505.PCA9505_MSK_PORTS[port])
    
if __name__ == '__main__':
    import board
    import busio
    i2c = busio.I2C (scl=board.GP5, sda=board.GP4)
    pca = PCA9505(i2c, 0b0100000) #0x20 A0=0 A1=0 A2=0
    pca.begin()
    pca.portMode(PCA9505.PORT0, PCA9505.INPUT)
    pca.portMode(PCA9505.PORT1, PCA9505.INPUT)
    pca.portMode(PCA9505.PORT2, PCA9505.INPUT)
    pca.portMode(PCA9505.PORT3, PCA9505.INPUT)
    pca.portMode(PCA9505.PORT4, PCA9505.INPUT)
    pca.portMode(PCA9505.PORT0, PCA9505.OUTPUT)
    pca.pinMode(0, PCA9505.OUTPUT)
    pca.pinMode(1, PCA9505.OUTPUT)
    
    x = False
    while True:
        pca.pinWrite(0, x)
        pca.pinWrite(1, not x)
        x=not x
        time.sleep(0.25)
        
        x0 = pca.portRead(PCA9505.PORT0)
        x1 = pca.portRead(PCA9505.PORT1)
        x2 = pca.portRead(PCA9505.PORT2)
        x3 = pca.portRead(PCA9505.PORT3)
        x4 = pca.portRead(PCA9505.PORT4)
        
        b0 = "{:#010b}".format(x0).replace("0b","")
        b1 = "{:#010b}".format(x1).replace("0b","")
        b2 = "{:#010b}".format(x2).replace("0b","")
        b3 = "{:#010b}".format(x3).replace("0b","")
        b4 = "{:#010b}".format(x4).replace("0b","")
        print(''.join(reversed(b0)),''.join(reversed(b1)),''.join(reversed(b2)),''.join(reversed(b3)),''.join(reversed(b4)))

