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

scrapers = {}
agents = {}
ads = {}

settings = {
    "notify_recent" : 3
}

# Get tasks
tasks = tasklib.load_tasks(tasks_file)

# Get processed ads
with open(ads_file, "r") as stream:
    ads = yaml.safe_load(stream)

scrapers = scraperlib.get_scrapers()
agents = agentlib.get_agents()

def main():
    parser = argparse.ArgumentParser()
    notify_group = parser.add_mutually_exclusive_group()
    notify_group.add_argument("-s", "--skip-notification", action="store_true", default=False)
    notify_group.add_argument("--notify-recent", type=int, default=settings["notify_recent"], help=f"Only notify only most recent \# of ads. Default is {settings['notify_recent']}")

    main_args = parser.add_mutually_exclusive_group()
    main_args.add_argument("-c", "--cron-job", nargs=2, metavar=('INTEGER','minutes|hours'))
    main_args.add_argument("-r", "--refresh-cron", action="store_true", help="Refresh cron with current task frequencies")
    main_args.add_argument("-p", "--prime-all-tasks", action="store_true", help="Prime all tasks. If tasks file was edited manually, prime all the ads to prevent large notification dump")
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
    task_add.add_argument("--prime-ads", type=bool, help="Prime ads file after creation. Will prompt if unset")

    task_delete = task_subparsers.add_parser("delete", help="Prime ads after creating task. Will prompt if unset")
    task_delete.add_argument("index", type=int)
    task_delete.add_argument("--skip-confirm", action="store_true", help="Do not ask for confirmation")
    task_list = task_subparsers.add_parser("list", help="List all tasks")

    args = parser.parse_args()


    if args.prime_all_tasks:
        prime_all_tasks(args)

    if args.refresh_cron:
        refresh_cron()

    if args.cron_job:
        cron_cmd(args.cron_job, not args.skip_notification)

    if args.cmd == "task":
       task_cmd(args)

def refresh_cron():
    cronlib.clear()
    for t in tasks:
        if cronlib.exists(t.frequency, t.frequency_unit):
            continue

        cronlib.add(t.frequency, t.frequency_unit)

def prime_all_tasks(args):
    for task in tasks:
        run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)

    save_ads()


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
    tasklib.list_tasks(tasks)

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

    tasks.append(task)
    tasklib.save_tasks(tasks, tasks_file)
    cronlib.add(args.frequency, args.frequency_unit)

    print ("Task added")

    prime = True
    if args.prime_ads == None:
        askprime = input("Would you like to prime ads now? [Y/n]")
        if askprime == "n":
            prime = False

    if prime:
        run_task(task, notify=not args.skip_notification, recent_ads=args.notify_recent)
        save_ads()

def task_delete_cmd(args):
    index = args.index

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

# recent_ads - only show the latest N ads, set to 0 to disable
def run_task(task, notify=True, recent_ads=0):
    print (ads)
    scraper_name = task.source
    scraper = scrapers[scraper_name]
    url = task.url
    exclude_words = task.exclude

    print(f"""Task: {task.name}
Source: {task.source}
URL: {task.url}""")

    if len(task.include):
        print(f"Including: {task.include}")

    if len(task.exclude):
        print(f"Excluding: {task.exclude}")

    all_ads = {}
    if scraper_name in ads:
        all_ads = ads[scraper_name]
 
    scraper.set_all_ads(all_ads)
    scraper.set_exclude_list(exclude_words)

    new_ads, ad_title = scraper.scrape_for_ads(url)

    info_string = f"Found {len(new_ads)} new ads" \
        if len(new_ads) != 1 else "Found 1 new ad"
    print(info_string)

    num_ads = len(new_ads)
    if notify and num_ads:
        i = 0

        ads_to_send = new_ads

        if recent_ads > 0:
            # only notify the last notify_recent new_ads
            ads_to_send = get_recent_ads(recent_ads, new_ads)
            print(f"Total ads being notified: {len(ads_to_send)}")

        for agent_id in agents:
            agent = agents[agent_id]
            agent.send_ads(ads_to_send, ad_title)
            i = i + 1


    print()

    ads[scraper_name] = scraper.id

def get_recent_ads(recent, ads):
    i = 0

    result = {}

    for a in ads:
        if i >= len(ads) - recent:
            result[a] = ads[a]

        i = i + 1

    return result

# This was run as a cronjob so find all tasks that match the schedule
# -c {cron_time} {cron_unit}
# cron_time: integer
# cron_unit: string [ minute | hour ]
def cron_cmd(cron_args, notify=True):
    cron_time = cron_args[0]
    cron_unit = cron_args[1]

    # Scrape each url given in tasks file
    for task in tasks:
        freq = task.frequency
        freq_unit = task.frequency_unit

        print(f"{freq} {freq_unit}:{cron_time} {cron_unit}")
        # skip tasks that dont correspond with the cron schedule
        if int(freq) != int(cron_time) or freq_unit[:1] != cron_unit[:1]:
            continue

        run_task(task, notify)

    save_ads()

def save_ads():
    with open(ads_file, "w") as stream:
        json.dump(ads, stream)

if __name__ == "__main__":
    main()

