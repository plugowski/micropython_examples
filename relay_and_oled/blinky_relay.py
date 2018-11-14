from machine import Pin
import time

relay_pin = Pin(12, Pin.OUT)
state = 0

while True:
    state = 1 if state == 0 else 0
    relay_pin.value(state)
    time.sleep(0.05)
