
import transfer.ws_manager as ws_manager
import transfer.udp_manager as udp_manager
import files.log_manager as log_manager
import time

class WebGLManager:
    def __init__(self):
        self.__ws_manager = ws_manager.WsManager()
        self.__log_manager = log_manager.LogManager("./log/")
        self.__udp_manager = udp_manager.UdpManager()


    def initialize(self):
        self.__ws_manager.initialize("ws://localhost:30001")
        self.__udp_manager.initialize("127.0.0.1", 50002)
        self.__udp_manager.set_handler(self.__ws_manager.send)

    def run(self):
        self.__udp_manager.run()
        # for frame in range(1230, 2430):
        #     data = self.__log_manager.read_logging_file(frame)
        #     self.__ws_manager.send(data)
        #     time.sleep(0.04)

    def shutdown(self):
        pass