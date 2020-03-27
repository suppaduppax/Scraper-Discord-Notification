#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect
import reflection_lib as refl

# looks for sub diretories inside "{directory}"
# and inspects its contents for a "agent.py" file and grabs the class inside that file
# uses config files inside of  {directory}/{agent_dir}/config.yaml
# RETURNS: a dictionary {agent_name : agent_instance}
def get_agents(directory, agent_dir):
    result = {}

    filename = "agent.py"
    config_file = "config.yaml"

    subdirs = refl.get_directories(f"{directory}/{agent_dir}")
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

        with open(f"{directory}/{agent_dir}/{subdir}/{config_file}", "r") as stream:
            config = yaml.safe_load(stream)

        result[module_class_name] = module_class(config)

    return result
