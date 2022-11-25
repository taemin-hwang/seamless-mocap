import socket

class UdpManager:
    def __init__(self):
        self.__server = None

    def initialize(self, host, port):
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.bind((host, port))

    def run(self):
        while True:
            data, addr = self.__server.recvfrom(65535)
            if self.__handler is not None:
                if data:
                    self.__handler(data)

    def set_handler(self, f):
        self.__handler = f

