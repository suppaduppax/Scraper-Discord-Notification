#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
#import json
import inspect

import reflection_lib as refl


# looks for sub diretories inside "scrapers/"
# and inspects its contents for a "scraper.py" file and grabs the class inside that file
# PARAMS: scraper_ads - json of all the previously scraped files
# RETURNS: a dictionary {scraper_name : scraper_instance} 
def get_scrapers():
    result = {}
    subdir = "scrapers"
    filename = "scraper.py"

    dirs = refl.get_directories(subdir)
    for dir in dirs:
        scraper_name = dir
        path = f"{subdir}/{dir}/{filename}"
        if not os.path.exists(path):
            continue

        namespace = refl.path_to_namespace(path)
        module = refl.get_module(namespace)
        module_class_name, module_class = refl.get_class(module, namespace)

        result[module_class_name] = module_class()

    return result
