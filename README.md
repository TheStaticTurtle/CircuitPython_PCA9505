# CircuitPython_PCA9505
A circuit python class to be a ble to use the PCA9505(6) chip

The PCA9505 is a 40pin gpio expander, the chip has 4 banks of 8 pins and supports interrupts.
Here is an example that fill blink the first two leds and print the state of the pins in the console
When set as input the chip will enable pullups on the lines (this only work on PCA9505 not the PCA9506)
```py
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
```
