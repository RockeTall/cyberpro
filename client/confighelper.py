import json
import sys
import os

class ConfigHelper:
    defaultdata = {
        "serverip": "127.0.0.1",
        "port": 6677
    }

    if getattr(sys, 'frozen', False):
        basepath = os.path.dirname(sys.executable)
    else:
        basepath = os.path.dirname(os.path.abspath(__file__))

    configpath = os.path.join(basepath, "config.json")

    @classmethod
    def loadconfig(cls):
        if not os.path.exists(ConfigHelper.configpath):
            print("Config not found")
            return dict(ConfigHelper.defaultdata)
        try:
            with open(ConfigHelper.configpath, "r") as f:
                config = json.load(f)
            data = dict(ConfigHelper.defaultdata)
            data.update(config)
            print(str(data))
            return data
        except Exception as e:
            print(f"error config: {e}")
            return dict(ConfigHelper.defaultdata)


