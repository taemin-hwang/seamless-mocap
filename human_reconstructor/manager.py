
from queue import Queue
import threading

from reconstructor import reconstructor as rc
from transfer import gui_sender, skeleton_server, facehand_server, unity_sender
from config import config_parser as cp

class Manager:
    def __init__(self, args):
        self.__args = args
        self.__reconstructor = rc.Reconstructor(self.__args)
        if self.__args.log:
            self.__config_parser = cp.ConfigParser(self.__args.log + 'config.json')
        else:
            self.__config_parser = cp.ConfigParser(self.__args.path + 'config.json')
        self.__gui_sender = gui_sender.GuiSender()
        self.__unity_sender = unity_sender.UnitySender()

    def initialize(self):
        config = self.__config_parser.GetConfig()
        self.__reconstructor.initialize(self.__config_parser)
        if self.__args.gui:
            self.__gui_sender.initialize(config["gui_ip"], config["gui_port"])
        if self.__args.unity:
            self.__unity_sender.initialize(config["unity_ip"], config["unity_port"])

    def run(self):
        self.__reconstructor.run(self.__recv_skeleton_from_edge, self.__recv_facehand_from_edge, self.__send_skeleton_to_gui, self.__send_skeleton_to_unity)

    def __recv_facehand_from_edge(self, ipaddr, port):
        facehand_server.execute(ipaddr, port)
        return facehand_server.message_queue, facehand_server.lock

    def __recv_skeleton_from_edge(self, ipaddr, port):
        skeleton_server.execute(ipaddr,port)
        return skeleton_server.message_queue, skeleton_server.lock

    def __send_skeleton_to_gui(self, data):
        self.__gui_sender.send_3d_skeletons(data)

    def __send_skeleton_to_unity(self, data):
        self.__unity_sender.send_3d_skeletons(data)