import yaml

def _get_defaults():
    s = {}
    s["gobal_include"] = []
    s["gobal_exclude"] = []
    s["recent_ads"] = 3
    s["log_rotation_files"] = 5
    return s

def load(file):
    global _settings

    _settings = _get_defaults()
    with open(file, "r") as stream:
        _settings = yaml.safe_load(stream)

def get(key):
    return _settings[key]

if __name__ == "__main__":
    print(load_settings("settings.yaml").__dict__)

