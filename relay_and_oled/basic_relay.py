from machine import Pin

relay_pin = Pin(12, Pin.OUT)
relay_pin.value(1)
