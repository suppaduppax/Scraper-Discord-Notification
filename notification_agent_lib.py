#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect
import reflection_lib as refl
import logger_lib as log
import uuid
import re

class notif_agent:
    enabled = True

    def __init__(self, id, name, module, module_properties):
        self.id = id
        self.name = name
        self.module = module
        self.module_properties = module_properties

# looks for sub diretories inside "{directory}"
# and inspects its contents for a "agent.py" file and grabs the class inside that file
# uses config files inside of  {directory}/{agent_dir}/config.yaml
# RETURNS: a dictionary {agent_name : agent_instance}
def get_modules(directory, agent_dir):
    result = {}
    filename = "agent.py"
    config_file = "config.yaml"

    subdirs = refl.get_directories(f"{directory}/{agent_dir}")
    modules = {}

    for subdir in subdirs:
        scraper_name = subdir
        path = f"{directory}/{agent_dir}/{subdir}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(f"{agent_dir}/{subdir}/{filename}")
        finder = importlib.machinery.PathFinder()
        spec = importlib.util.find_spec(f"{namespace}")
        #spec = importlib.machinery.find_spec(f"{path}")
        module = importlib.util.module_from_spec(spec)
#        sys.modules[module_name] = module
        spec.loader.exec_module(module)

#        namespace = refl.path_to_namespace(path)
#        module = refl.get_module(namespace)
        module_class_name, module_class = refl.get_class(module, namespace)
        result[subdir] = module_class()

    return result

def get_agents(directory, agents_file, modules_dir):
    modules = get_modules(directory, modules_dir)
    result = {}

    with open(f"{directory}/{agents_file}", "r") as stream:
        config = yaml.safe_load(stream)


    for c in config:
        agent = notif_agent(
                    c.get("id", str(uuid.uuid4())),
                    c.get("name"),
                    c.get("module"),
                    c.get("module_properties")
                )

        agent.enabled = c.get("enabled", True)

        log.debug(f"Adding notification agent: {agent.id} {agent.name}")
        result[agent.id] = agent

    return result

def get_notif_agents_by_ids(notif_agents, ids):
    print (ids)
    result = []
    for id in ids:
        print (f"{id}: enabled: {notif_agents[id].enabled}")
        result.append(notif_agents[id])

    return result


def get_names(notif_agents):
    names = []
    for a in notif_agents:
        names.append(a.name)

    return names

def get_enabled(agents):
    print (agents)
    result = []
    for a in agents:
        if a.enabled:
            result.append(a)

    return result

# <-- don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop

def save(notif_agents, file, preserve_comments=False):
    if isinstance(notif_agents, dict):
        old_notif_agents = notif_agents
        notif_agents = []
        for s in old_notif_agents:
            notif_agents.append(old_notif_agents[s])

    elif isinstance(notif_agents, list) == False:
        raise ValueError(f"notif_agents must by list or dict, not: {type(notif_agents)}")


    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(notif_agents, stream, default_flow_style=False, sort_keys=False)
