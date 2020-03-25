#!/usr/bin/env python3

# main.py -h for help
# main.py --cron-job help
# main.py task -h
# main.py task [add|delete|list] -h for more help!

import yaml
import sys
import os
import importlib
import json
import inspect
import argparse

import notification_agent_lib as agentlib
import scraper_lib as scraperlib
import reflection_lib as refl
import task_lib as tasklib
import cron_lib as cronlib

current_directory = os.path.dirname(os.path.realpath(__file__))
ads_file = current_directory + "/ads.json"
tasks_file = current_directory + "/tasks.yaml"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--skip-notification", action="store_true", default=False)

    main_args = parser.add_mutually_exclusive_group()
    main_args.add_argument("-c", "--cron-job", nargs=2, metavar=('INTEGER','minutes|hours'))
    main_subparsers = parser.add_subparsers(dest="cmd")

    # task {name} {frequency} {frequency_unit}
    main_sub = main_subparsers.add_parser("task")
    task_subparsers = main_sub.add_subparsers(dest="task_cmd", required=True)
#    main_sub.add_argument("task_cmd", choices=["add", "delete", "list"])
    task_add = task_subparsers.add_parser("add", help="Add a new task")
    task_add.add_argument("-n", "--name", default="Untitled Task")
    task_add.add_argument("-s", "--source", required=True)
    task_add.add_argument("-u", "--url", required=True)
    task_add.add_argument("-f", "--frequency", type=int, required=True)
    task_add.add_argument("-F", "--frequency_unit", choices=["minutes", "hours"], required=True)
    task_add.add_argument("-i", "--include", nargs="+", default=[], required=True)
    task_add.add_argument("-x", "--exclude", nargs="+", default=[])
    task_add.add_argument("--skip-confirm", action="store_true", help="Do not ask for confirmation")

    task_delete = task_subparsers.add_parser("delete", help="Delete a task by index. Use task list to show indices")
    task_delete.add_argument("index", type=int)
    task_delete.add_argument("--skip-confirm", action="store_true", help="Do not ask for confirmation")
    task_list = task_subparsers.add_parser("list", help="List all tasks")

    args = parser.parse_args()

    if args.cron_job:
        cron_cmd(args.cron_job, args.skip_notification)

    if args.cmd == "task":
       task_cmd(args)


def task_cmd(args):
    cmds = {
        "add" : task_add_cmd,
        "delete" : task_delete_cmd,
        "list" : task_list_cmd
    }

    if args.task_cmd in cmds:
        cmds[args.task_cmd](args)
    else:
        print(f"Unknown task command: {args.args_cmd}")

def task_list_cmd(args):
    tasklib.list_tasks_in_file(tasks_file)

def task_add_cmd(args):
    task = tasklib.Task(\
        name = args.name,\
        frequency = args.frequency,\
        frequency_unit = args.frequency_unit,\
        source = args.source,\
        url = args.url,\
        include = args.include,\
        exclude = args.exclude\
    )

    if args.skip_confirm != True:
        tasklib.print_task(task)
        confirm = input("Add this task? [Y/n] ").lower()
        if confirm == "n":
            print ("Canceled")
            return

    tasklib.append_task_to_file(task, tasks_file)
    cronlib.add(args.frequency, args.frequency_unit)

    print ("Task added")

def task_delete_cmd(args):
    index = args.index
    print(args)
    tasks = tasklib.load_tasks(tasks_file)
    if index < 0 or index >= len(tasks):
        print(f"task delete: index must be 0-{len(tasks)-1}")
        return

    if args.skip_confirm != True:
        tasklib.print_task(tasks[index])
        confirm = input("Delete this task? [y/N] ").lower()
        if confirm != "y":
            print ("Canceled")
            return

    freq = tasks[index].frequency
    freq_unit = tasks[index].frequency_unit

    del(tasks[index])
    tasklib.save_tasks(tasks, tasks_file)

    # clear cronjob if no remaining tasks share the frequency
    freq_found = False
    for task in tasks:
        if task.matches_freq(freq, freq_unit):
            freq_found = True

    if freq_found == False:
        cronlib.delete(freq, freq_unit)

    print(f"Deleted task [{index}]")

# This was run as a cronjob so find all tasks that match the schedule
# -c {cron_time} {cron_unit}
# cron_time: integer
# cron_unit: string [ minute | hour ]
def cron_cmd(cron_args, skip_flag=False):
    cron_time = cron_args[0]
    cron_unit = cron_args[1]

    scrapers = {}
    agents = {}
    ads = {}

    # Get tasks
    with open(tasks_file, "r") as stream:
        tasks = yaml.safe_load(stream)

    # Get processed ads
    with open(ads_file, "r") as stream:
        ads = yaml.safe_load(stream)

    scrapers = scraperlib.get_scrapers(ads)
    agents = agentlib.get_agents()

    # Scrape each url given in tasks file
    for task in tasks:
        freq = task.get("frequency")
        freq_unit = task.get("frequency_unit")

        print(f"{freq} {freq_unit}:{cron_time} {cron_unit}")
        # skip tasks that dont correspond with the cron schedule
        if int(freq) != int(cron_time) or freq_unit[:1] != cron_unit[:1]:
            continue

        scraper_name = task.get("source")
        scraper = scrapers[scraper_name]
        url = task.get("url")
        exclude_words = task.get("easdfasdfxclude", [])

        print(f"Scraping: {url}")

        if len(exclude_words):
            print("Excluding: " + ", ".join(exclude_words))

        scraper.set_exclude_list(exclude_words)
        ads, ad_title = scraper.scrape_for_ads(url)

        info_string = f"Found {len(ads)} new ads\n" \
            if len(ads) != 1 else "Found 1 new ad\n"
        print(info_string)

        if not skip_flag and len(ads):
            for agent_id in agents:
                agent = agents[agent_id]
                agent.send_ads(ads, ad_title)

        ads[scraper_name] = scraper.id

    with open(ads_file, "w") as stream:
        json.dump(ads, stream)

if __name__ == "__main__":
    main()

