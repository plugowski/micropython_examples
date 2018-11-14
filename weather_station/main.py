from machine import Pin, I2C, ADC, deepsleep, RTC, DEEPSLEEP
from network import WLAN, STA_IF
from bh1750 import BH1750
from bme280 import BME280, BME280_OSAMPLE_16
from ssd1306 import SSD1306_I2C
from dht import DHT11
from math import floor
import urequests
import utime

# set i2c bus
i2c = I2C(sda=Pin(4), scl=Pin(5))
devices = i2c.scan()

# setup all devices
display = None if 0x3c not in devices else SSD1306_I2C(128, 64, i2c)
light_sensor = None if 0x23 not in devices else BH1750(i2c)
bme = None if 0x76 not in devices else BME280(i2c=i2c, mode=BME280_OSAMPLE_16)
dht = DHT11(Pin(14))
# adc = ADC(0)

adafruit_url = 'https://io.adafruit.com/api/v2/plugowski/groups/micrometeo/data'


def show(method: str, *args):
    if display is not None:
        getattr(display, method)(*args)
    elif method == 'text':
        print(args[0])


def justify_right(value, y):
    x = 128 - (8 * len(str(value)))
    show('text', str(value), x, y)


# connect to local network
wifi_ssid = b'SSID'
wifi_pass = b'PASS'
wifi = WLAN(STA_IF)
wifi.active(True)
available_networks = wifi.scan()

is_network = False
for ntwrk in available_networks:
    if ntwrk[0] == wifi_ssid:
        is_network = True

if is_network:
    wifi.connect(wifi_ssid, wifi_pass)
    while not wifi.isconnected():
        utime.sleep_ms(200)
else:
    wifi.disconnect()
    wifi.active(False)

dht.measure()
humidity = dht.humidity()
luminance = None if light_sensor is None else floor(light_sensor.luminance(BH1750.ONCE_HIRES_2))
# for some reason for correct pressure value, the temp should be called first!
temperature = None if bme is None else round(bme.temperature, 1)
pressure = None if bme is None else floor(bme.pressure / 100)

# jezeli ustawiony wyswietlacz
show('fill', 0)
show('text', 'Lux:', 0, 0)
justify_right(luminance, 0)
show('text', 'Tmp:', 0, 10)
justify_right(str(dht.temperature()) + ' / ' + str(temperature) + ' C', 10)
show('text', 'P: ', 0, 20)
justify_right(str(pressure) + ' hPa', 20)
show('text', 'RH', 0, 30)
justify_right(str(humidity) + ' %', 30)
show('line', 0, 52, 128, 52, 1)
justify_right(wifi.ifconfig()[0], 56)
show('show')
utime.sleep(2)

if wifi.isconnected():
    feed_data = [{'key': 'humidity', 'value': humidity}]
    if bme is not None:
        feed_data.append({'key': 'pressure', 'value': pressure})
        feed_data.append({'key': 'temperature', 'value': dht.temperature()})
    else:
        feed_data.append({'key': 'temperature', 'value': dht.temperature()})

    if light_sensor is not None:
        feed_data.append({'key': 'luminance', 'value': luminance})

    request = urequests.post(adafruit_url, json={'feeds': feed_data}, headers={'X-AIO-Key': 'b4a84d8373a447c1b9140167b3bb2f4d'})

rtc = RTC()
rtc.irq(trigger=RTC.ALARM0, wake=DEEPSLEEP)
rtc.alarm(RTC.ALARM0, 300000)
deepsleep()
