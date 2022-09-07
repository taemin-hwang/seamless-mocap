import json

class ConfigParser:
    def __init__(self, file):
        self.config_json = {}
        self.config_json["cam_num"] = 4
        self.config_json["min_cam"] = 3
        self.config_json["max_frame"] = 50
        self.config_json["fps"] = 20
        self.config_json["min_confidence"] = 0.0

        self.file = file
        with open(file, "r") as config_file:
            config_json = json.load(config_file)
        self.config_json = config_json
        print("[CONFIG] NUM OF CAM :", config_json["cam_num"])
        print("[CONFIG] MIN CAM    :", config_json["min_cam"])
        print("[CONFIG] MAX FRAME  :", config_json["max_frame"])
        print("[CONFIG] TARGET FPS :", config_json["fps"])
        print("[CONFIG] MIN CONFID :", config_json["min_confidence"])

    def GetConfig(self):
        if len(self.config_json) == 0:
            print("[WARN] cannot read config.json")
        return self.config_json

    def WriteMaxPersonNum(self, max_person_num):
        self.config_json["max_person"] = max_person_num
        with open(self.file, "w") as config_file:
            json.dump(self.config_json, config_file)