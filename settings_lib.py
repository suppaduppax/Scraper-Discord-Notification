import yaml

class Settings:
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

        return s

def load_settings(file):
    with open(file, "r") as stream:
        settings = yaml.safe_load(stream)

    return Settings.load(settings)

if __name__ == "__main__":
    print(load_settings("settings.yaml").__dict__)

