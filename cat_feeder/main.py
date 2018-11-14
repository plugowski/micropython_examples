from cat_feeder import CatFeeder
import socket_server
from ssd1306 import SSD1306_I2C
from machine import Pin, PWM, I2C
import network
import uasyncio as asyncio

# setup WiFi
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=b"CatFeeder", authmode=network.AUTH_WPA_WPA2_PSK, password=b"CatFeeder123")

# ustawienia wyswietlacza
i2c = I2C(scl=Pin(4), sda=Pin(5))
oled = SSD1306_I2C(128, 64, i2c)

# pulse-width modulation pin
pwm = PWM(Pin(16))

# fizyczny przycisk wyzwalacza
button = Pin(14, Pin.IN)

cat_feeder = CatFeeder(pwm, button, oled)

button.irq(trigger=Pin.IRQ_FALLING, handler=cat_feeder.auto_feed)

server = socket_server.SliderServer(cat_feeder)
server.start()
# initialize asyncio loop
loop = asyncio.get_event_loop()

loop.call_soon(server.process_all())

loop.run_forever()
server.stop()
