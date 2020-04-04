"""

"""

import yaml
import collections
import subprocess
import re

minute="minute"
hour="hour"
day="day"

class Task:
    yaml_tag = None

    def __init__(self, **kwargs):
            self.name = kwargs.get("name", "New Task")
            self.enabled = kwargs.get("enabled", True)
            self.frequency = kwargs.get("frequency", 15)
            self.frequency_unit = kwargs.get("frequency_unit", "minutes")
            self.source_ids = kwargs.get("source_ids", [])
            self.notif_agent_ids = kwargs.get("notif_agent_ids", [])
            self.include = kwargs.get("include", [])
            self.exclude = kwargs.get("exclude", [])

    def set_frequency(freq, unit):
        self.frequency = freq
        self.frequency_unit = unit

    def yaml(self):
        return yaml.dump(self.__dict)

    @staticmethod
    def load(data):
        values = data
        #print(values)

        if "exclude" in values:
            exclude = values["exclude"]
        else:
            exclude = []


        return Task(**data)

    def matches_freq(self, time, unit):
        return time == self.frequency and unit[:1] == self.frequency_unit[:1]

def load_tasks(file):
    with open(file, "r") as stream:
        tasks_yaml = yaml.safe_load(stream)

    tasks = []
    for t in tasks_yaml:
        tasks.append(Task.load(t))

    return tasks

def list_tasks_in_file(file):
    list_tasks(load_tasks(file))

def list_tasks(tasks):
    i = 0
    for t in tasks:
        print (f"[{i}]")
        print_task(t)
        i = i+1

def save(tasks, file, preserve_comments=True):
    if preserve_comments:
        # preserve comments in file
        with open(file, "r") as stream:
            filestream = stream.read()

        match = re.findall("([#][^\n]*[\n]|[#][\n])", filestream)

    with open(file, "w") as stream:
        if preserve_comments and match:
            for m in match:
                stream.write(m)

        yaml.dump(tasks, stream, default_flow_style=False, sort_keys=False)

def append_task_to_file(task, file):
    tasks = load_tasks(file)
    tasks.append(task)
    save_tasks(tasks, file)

def delete_task_from_file(index, file):
    tasks = load_tasks(file)
    if index < 0 or index >= len(tasks):
        logging.error(f"tasklib.delete_task_from_file: Invalid index: {index}")
        return

    del(tasks[index])
    save_tasks(tasks, file)

def print_task(task):
        print(f"""Name: {task.name}
Source ids: {task.source_ids}
Frequency: {task.frequency} {task.frequency_unit}
Url: {task.url}
Include: {task.include}
Exclude: {task.exclude}
""")

# <-- don't output yaml class tags
def noop(self, *args, **kw):
    pass

yaml.emitter.Emitter.process_tag = noop
# --------------------------------------->

if __name__ == "__main__":
    t = load_tasks("tasks.yaml")
    save_tasks(t, "tasks.yaml", "tasks.yaml")

