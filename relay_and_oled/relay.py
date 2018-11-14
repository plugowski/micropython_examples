import relay_socket
import network
import uasyncio as asyncio
from machine import Pin

relay_pin = Pin(12, Pin.OUT)
server = None


def run():
    global server
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=b"Relay", authmode=network.AUTH_OPEN)

    server = relay_socket.Server(relay_pin)
    server.start()

    loop = asyncio.get_event_loop()

    loop.call_soon(server.process_all())

    loop.run_forever()
    server.stop()
