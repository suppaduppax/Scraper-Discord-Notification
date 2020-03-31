#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect
import reflection_lib as refl
import logger_lib as log

class notif_agent:
    enabled = True
    def __init__(self, name, module_class, module_properties):
        self.name = name
        self.module_class = module_class
        self.module_properties = module_properties
        self.load_module()

    def load_module(self):
        if not self.module_class or not self.module_properties:
            log.error_print("Cannot create notification agent module. Module class or module properties is empty or undefined")
            return

        self.module = self.module_class(self.module_properties)

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
        result[subdir] = module_class

    return result

def get_agents(directory, agents_file, modules_dir):
    modules = get_modules(directory, modules_dir)
    result = []

    with open(f"{directory}/{agents_file}", "r") as stream:
        config = yaml.safe_load(stream)


    for c in config:
        agent = notif_agent(
                    c.get("name"),
                    modules[c.get("module")],
                    c.get("module_properties")
                )

        agent.enabled = c.get("enabled", True)
        result.append(agent)

    return result


def get_enabled(agents):
    result = []
    for a in agents:
        if a.enabled:
            result.append(a)

    return result
