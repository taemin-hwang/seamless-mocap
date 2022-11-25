import websocket
import ssl

class WsManager:
    def __init__(self):
        self.__frame = 0
        self.__ws = None
        self.__url = None

    def __del__(self):
        if self.__ws is not None:
            self.__ws.close()

    def initialize(self, url):
        self.__url = url
        self.__ws = self.__try_to_connect_websocket()

    def send(self, data):
        try:
            # if self.__frame % 10 == 0 or self.__frame % 10 == 1:
            ret = self.__ws.send(data)
        except Exception as e:
            print(str(e))
            self.__ws = self.__try_to_connect_websocket()

    def __try_to_connect_websocket(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        ws = websocket.WebSocket()
        if self.__url is not None:
        # url = "ws://localhost:30001"
            ws.connect(self.__url, ssl=ssl_context)
        else:
            print('url is not initialized!')
        return ws
