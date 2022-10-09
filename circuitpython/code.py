import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import digitalio
import usb_hid
from adafruit_hid.mouse import Mouse

AZ1UBALL_ADDR = 10

i2c = busio.I2C(board.GP9, board.GP8)
mouse = Mouse(usb_hid.devices)
btn0 = digitalio.DigitalInOut(board.GP20)
btn0.direction = digitalio.Direction.INPUT
btn0.pull = digitalio.Pull.DOWN
btn1 = digitalio.DigitalInOut(board.GP21)
btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.DOWN


def check_i2c():
    i2c.try_lock()
    try:
        if AZ1UBALL_ADDR not in i2c.scan():
            raise Exception("does not find azball")
    finally:
        i2c.unlock()


def setup_ball():
    with I2CDevice(i2c, AZ1UBALL_ADDR) as d:
        d.write(b"\x91")


def scan_ball(buf: bytearray):
    with I2CDevice(i2c, AZ1UBALL_ADDR) as d:
        d.readinto(buf)



def main():
    check_i2c()
    setup_ball()

    ball_pressed = False
    left_pressed = False
    right_pressed = False

    buf = bytearray(5)
    while True:
        scan_ball(buf)
        multi = 10
        x = (buf[2] - buf[3])
        y = (buf[1] - buf[0])
        ball_click = buf[4] == 0x80
        left_button = btn1.value
        right_button = btn0.value

        # print(buf[0], buf[1], buf[2], buf[3], ball_click, right_button, left_button)

        if ball_click != ball_pressed:
            if ball_click:
                mouse.press(Mouse.RIGHT_BUTTON)
            else:
                mouse.release(Mouse.RIGHT_BUTTON)
            ball_pressed = ball_click

        if left_button != left_pressed:
            left_pressed = left_button

        if right_button != right_pressed:
            if right_button:
                mouse.press(Mouse.LEFT_BUTTON)
            else:
                mouse.release(Mouse.LEFT_BUTTON)
            right_pressed = right_button

        if not ball_pressed and not left_pressed:
            mouse.move(x=x*multi, y=y*multi)
        if left_pressed:
            mouse.move(wheel=-1*y)

        time.sleep(0.02)


main()
