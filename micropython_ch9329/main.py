import machine
from machine import Pin, I2C, UART

i2c = I2C(0, scl=Pin(5), sda=Pin(4))
ch9329 = UART(0, baudrate=9600, bits=8, parity=None, tx=Pin(0), rx=Pin(1))

ADDR = 10


def check_i2c():
    if ADDR not in i2c.scan():
        raise Exception("does not find azball")


def scan():
    b = i2c.readfrom(ADDR, 5)
    return b


def setup():
    i2c.writeto(ADDR, b"\x91")


def mouse_act_byte(x: int, y: int, scroll: int, click: bool) -> bytes:
    if(x>127):
        x=127
    if(x<-128):
        x=-128
    if(y>127):
        y=127
    if(y<-128):
        y=-128
    b=[0x57,0xab,0x00,0x05,0x05,0x01]
    b.append(0x00 + int(click))
    if(x<0):
        x=0x100+x
    if(y<0):
        y=0x100+y
    b.append(x)
    b.append(y)
    b.append(scroll)
    s=sum(b) & 0xff
    b.append(s)

    return bytes(b)


def main():
    check_i2c()
    setup()

    while True:
        b = scan()
        multi = 10
        x = (b[2] - b[3]) * multi
        y = (b[1] - b[0]) * multi
        button = b[4] == 0x80
        code = mouse_act_byte(x, y, 0, button)
        # print(b[0], b[1], b[2], b[3], b[4], "".join("\\x%02x" % i for i in code))
        ch9329.write(code)
        machine.lightsleep(20)

main()
