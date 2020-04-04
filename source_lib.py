"""

"""

import yaml
import collections
import subprocess
import re
import uuid

class Source:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", str(uuid.uuid4()))
        self.name = kwargs.get("name", "New Source")
#        self.url = kwargs.get("url", "")
        self.module = kwargs.get("module")
        self.module_properties = kwargs.get("module_properties")
    @staticmethod
    def load(data):
        values = data
        #print(values)

        return Source(**data)

def load(file):
    with open(file, "r") as stream:
        sources_yaml = yaml.safe_load(stream)

    sources = {}
    for s in sources_yaml:
        source = Source.load(s)
        sources[source.id] = source

    return sources

def list_sources_in_file(file):
    list_sources(load_sources(file))

def list_sources(sources):
    i = 0
    for t in sources:
        print (f"[{i}]")
        print_source(t)
        i = i+1

def save(sources, file, preserve_comments=True):
    if isinstance(sources, dict):
        old_sources = sources
        sources = []
        for s in old_sources:
            sources.append(old_sources[s])

    elif isinstance(sources, list) == False:
        raise ValueError(f"sources must by list or dict, not: {type(sources)}")


    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(sources, stream, default_flow_style=False, sort_keys=False)

def appnd_source_to_file(source, file):
    sources = load_sources(file)
    sources.append(source)
    save_sources(sources, file)

def delete_source_from_file(index, file):
    sources = load_sources(file)
    if index < 0 or index >= len(sources):
        logging.error(f"sourcelib.delete_source_from_file: Invalid index: {index}")
        return

    del(sources[index])
    save_sources(sources, file)

def print_source(source):
        print(f"""Name: {source.name}
Source: {source.source}
Frequency: {source.frequency} {source.frequency_unit}
Url: {source.url}
Include: {source.include}
Exclude: {source.exclude}
""")

# <-- don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop
# --------------------------------------->

if __name__ == "__main__":
    t = load_sources("sources.yaml")
    save_sources(t, "sources.yaml", "sources.yaml")

