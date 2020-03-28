import yaml

class Settings:
    log_file_rotation = 5

    global_include = []
    global_exclude = []
    recent_ads = []

    def __init__(self):
        return

    @staticmethod
    def load(data):
        s = Settings()
        if "global_include" in data:
            s.global_include = data["global_include"]

        if "global_exclude" in data:
            s.global_exclude = data["global_exclude"]

        s.recent_ads = data["recent_ads"]
        s.log_file_rotation = data["log_file_rotation"]
        return s

def load(file):
    global _settings
    with open(file, "r") as stream:
        _settings = yaml.safe_load(stream)

def get(key):
    return _settings[key]

if __name__ == "__main__":
    print(load_settings("settings.yaml").__dict__)

