import ujson
from uwebsocket import *
from machine import Pin


class Client(WebSocketClient):

    response = {
        "msg": "",
        "state": 0
    }

    def __init__(self, conn, pin: Pin):
        self.pin = pin
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()

            if not msg:
                return

            msg = msg.decode("utf-8")
            command = ujson.loads(msg)

            if command['action'] == 'switch':
                state = 0 if self.pin.value() == 1 else 1
                self.pin.value(state)

                self.response["state"] = state
                self.response["msg"] = "swieci" if state == 1 else "zgaszone"
                self.connection.write(ujson.dumps(self.response))

        except ValueError:
            self.connection.write('Wrong command!')

        except ClientClosedError:
            self.connection.close()


class Server(WebSocketServer):

    def __init__(self, pin: Pin):
        self.pin = pin
        super().__init__(2)

    def _make_client(self, conn):
        return Client(conn, self.pin)
