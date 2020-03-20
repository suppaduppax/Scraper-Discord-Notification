#!/usr/bin/env python3

import yaml
import sys
import os
import importlib
import json

class Scraper():
    enabled = False

    def __init__(self, name, path, ad_path, enabled, ads={}):
        self.name = name
        self.path = path
        self.ad_path = ad_path
        self.enabled = enabled

        if self.enabled == True:
            module_path = self.path.replace("/", ".") 
            module_path = module_path.replace(".py", "")

            # dynamically import module and store the scraper class
            self.module = importlib.import_module(module_path)
            scraper_class = getattr(self.module, self.name)
            self.scraper = scraper_class(ads)

            ad_module_path = self.ad_path.replace("/", ".")
            ad_module_path = module_path.replace(".py", "")

            self.ad_module = importlib.import_module(ad_module_path)
            ad_class = getattr(self.ad_module, self.name)
            self.ad = ad_class()

class Client():
    def __init__(self, name, path, config, enabled):
        self.name = name
        self.path = path
        self.enabled = enabled

        if enabled == True:
            module_path = self.path.replace("/", ".")
            module_path = module_path.replace(".py", "")

            # dynamically import module and store the client class
            self.module = importlib.import_module(module_path)
            client_class = getattr(self.module, self.name)
            self.client = client_class(config)


if __name__ == "__main__":
    args = sys.argv
    skip_flag = "-s" in args
    current_directory = os.path.dirname(os.path.realpath(__file__))
    ads_path = current_directory + "/ads.json"

    scrapers = {}
    clients = {}
    ads_dict = {}

    # Get config values
    with open(current_directory + "/config.yaml", "r") as stream:
        config = yaml.safe_load(stream)

    # Get scrapers
    print("Initializing Scrapers:")
    with open(current_directory + "/scrapers.yaml", "r") as stream:
        scrapers_config = yaml.safe_load(stream)

    if os.path.exists(ads_path):
        with open(ads_path, "r") as stream:
            ads_dict = json.load(stream)
    else:
        print("ads.json file not found! Creating: " + ads_path)
        with open(ads_path, "w") as stream:
            stream.write("{}")

    for scrapers_dict in scrapers_config:
        scraper_name = scrapers_dict.get("name")
        scraper_path = scrapers_dict.get("scraper_path")
        scraper_adpath = scrapers_dict.get("ad_path")
        scraper_enabled = scrapers_dict.get("enabled")

        print(f"- {scraper_name}")

        if scraper_name in ads_dict:
            # see if theres an ads entry for this scraper
            scraper_ads = ads_dict[scraper_name]
        else:
            scraper_ads = {}

        scrapers[scraper_name] = Scraper(scraper_name, scraper_path, scraper_adpath, scraper_enabled, scraper_ads)

    # Get clients
    print("Initializing Clients:")

    with open(current_directory + "/clients.yaml", "r") as stream:
        clients_config = yaml.safe_load(stream)

    for clients_dict in clients_config:
        client_name = clients_dict.get("name")
        client_path = clients_dict.get("path")
        client_enabled = clients_dict.get("enabled")
        client_config_path = clients_dict.get("config")

        print(f"- {client_name}")

        with open(current_directory + "/" + client_config_path, "r") as stream:
            client_config = yaml.safe_load(stream)

        # add client to clients dict
        clients[client_name] = Client(client_name, client_path, client_config, client_enabled)

    # Scrape each url given in config file
    for config_scraper in config:
        scraper=scrapers[config_scraper.get("scraper")]

        if scraper.enabled == False:
            continue

        for url_dict in config_scraper.get("urls"):
            url = url_dict.get("url")
            exclude_words = url_dict.get("exclude", [])
            print(f"Scraping: {url}")

            if len(exclude_words):
                print("Excluding: " + ", ".join(exclude_words))

            scraper.scraper.set_exclude_list(exclude_words)
            ads, ad_title = scraper.scraper.scrape_for_ads(url)

            info_string = f"Found {len(ads)} new ads\n" \
                if len(ads) != 1 else "Found 1 new ad\n"
            print(info_string)

            if not skip_flag and len(ads):
                for client_id in clients:
                    client = clients[client_id].client
                    if client.enabled == True:
                        client.send_ads(ads, ad_title)

        ads_dict[scraper.name] = scraper.scraper.id

        with open(ads_path, "w") as ads_file:
            json.dump(ads_dict, ads_file)
