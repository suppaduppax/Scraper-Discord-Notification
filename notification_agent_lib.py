#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect
import reflection_lib as refl

# looks for sub diretories inside "notification_agents/"
# and inspects its contents for a "agent.py" file and grabs the class inside that file
# uses config files inside of  /notication_agents/{agent_dir}/config.yaml
# RETURNS: a dictionary {agent_name : agent_instance}
def get_agents():
    result = {}
    subdir = "notification_agents"
    filename = "agent.py"
    config_file = "config.yaml"

    dirs = refl.get_directories(subdir)
    for dir in dirs:
        scraper_name = dir
        path = f"{subdir}/{dir}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(path)
        module = refl.get_module(namespace)
        module_class_name, module_class = refl.get_class(module, namespace)

        with open(f"{subdir}/{dir}/{config_file}", "r") as stream:
            config = yaml.safe_load(stream)

        result[module_class_name] = module_class(config)

    return result
