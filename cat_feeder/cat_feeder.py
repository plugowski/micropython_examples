import time
from ssd1306 import SSD1306_I2C
from machine import PWM, Pin
from uwebsocket import WebSocketConnection


class CatFeeder:

    # servo values for specified actions
    open = 200
    close = 700
    # state value
    state = 0

    def __init__(self, pwm: PWM, action_button: Pin, oled: SSD1306_I2C):

        # konfiguracja pwm i ustawienie w pozycji zamknietej
        pwm.freq(500)
        pwm.duty(self.close)
        pwm.deinit()

        self.pwm = pwm
        self.action_button = action_button
        self.oled = oled

        self.display_write('Initialized...')

    async def send_status(self, connection: WebSocketConnection):
        stan_slownie = ('otwarty' if self.state == 1 else 'zamkniety')
        connection.write("Aktualny status: " + stan_slownie)
        self.display_write('Status: ' + stan_slownie)

    def display_write(self, text: str):
        self.oled.fill(0)
        self.oled.text(text, 0, 0)
        self.oled.show()

    def feed(self):
        self.pwm.init()
        self.pwm.duty(self.open)
        time.sleep(0.4)
        self.pwm.deinit()
        self.state = 1

    def stop(self):
        self.pwm.init()
        self.pwm.duty(self.close)
        time.sleep(0.4)
        self.pwm.deinit()
        self.state = 0

    def auto_feed(self, irq: Pin = None):
        """ Automatyczny feeder - otwarcie + zamkniecie wylotu
        """
        self.feed()
        time.sleep(0.5)
        self.stop()
