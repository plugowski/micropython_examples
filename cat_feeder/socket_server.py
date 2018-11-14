import ujson
from uwebsocket import *
import uasyncio as asyncio
from cat_feeder import CatFeeder


class CatFeederClient(WebSocketClient):

    def __init__(self, conn, cat_feeder: CatFeeder):
        self.cat_feeder = cat_feeder
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()

            if not msg:
                return

            msg = msg.decode("utf-8")
            command = ujson.loads(msg)

            if command['action'] == 'feed':
                self.cat_feeder.feed()
            elif command['action'] == 'stop':
                self.cat_feeder.stop()

            # wysylka statusu do socketa
            asyncio.get_event_loop().create_task(self.cat_feeder.send_status(self.connection))

        except ValueError:
            self.connection.write('Wrong command!')

        except ClientClosedError:
            self.connection.close()


class SliderServer(WebSocketServer):

    def __init__(self, cat_feeder: CatFeeder):
        self.cat_feeder = cat_feeder
        super().__init__(2)

    def _make_client(self, conn):
        return CatFeederClient(conn, self.cat_feeder)
