import source_lib as sourcelib
import scraper_lib as scraper
import task_lib as tasklib

import uuid
import re
import logger_lib as log

def delete_task(tasks_list, file):
    while True:
        for i in range(len(tasks_list)):
            print(f"{i} - {tasks_list[i].name}")

        print ("(s)ave, (q)uit without saving")
        tnum_str = prompt_string("Delete task")
        if tnum_str == "s":
            tasklib.save(tasks_list, file)
            return
        elif tnum_str == "q":
            return

        if re.match("[0-9]+$", tnum_str):
            tnum = int(tnum_str)
            if tnum >= 0 and tnum < len(tasks_list):
                if yes_no(f"Are you sure you want to delete {tasks_list[tnum].name}") == "y":
                    del tasks_list[tnum]

def prompt_num(msg, force_positive=True, default=None):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    while True:
        num_str = input(f"{msg}:{default_str} ")
        if num_str == "":
            if default is not None:
                return default

        if re.match("[0-9]+$", num_str):
            num = int(num_str)
            return num

def prompt_range(msg, min, max, default=None, extra_options=None, allow_abbrev=True):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    range_str = ""
    range_num = None

    if min >= 0:
        if max == min:
            range_str = [min]
            range_num = min
        elif max > min:
            range_str = f" [{min}-{max}]"

    while True:
        num_str = input(f"{msg}{range_str}: {default_str}")
        if num_str == "":
            if default is not None:
                return default

        if extra_options is not None and allow_abbrev:
            found = None
            ambiguous = False
            for num_str in extra_options:
                if check in o:
                    if found is not None:
                        print(f"{check} is too ambiguous, try a longer abbreviation")
                        ambiguous = True
                        break

                    found = o

            if not ambiguous:
                return found

        if re.match("[0-9]+$", num_str):
            num = int(num_str)
            if num >= min and num <= max:
                return num

def prompt_options(msg, options, default=None, print_options=True, case_sens=False, allow_abbrev=True):
    default_str = ""

    if default is not None:
        default_str = f" [{default}]"

    if case_sens == False:
        for i in range(len(options)):
            options[i] = options[i].lower()

    choices = "/".join(options)

    result = None
    while True:
        result = input(f"{msg} [{choices}]:{default_str} ")
        check = result

        if result == "":
            if default is not None:
                return default
            else:
                continue

        if not case_sens:
            check = check.lower()

        if allow_abbrev:
            found = None
            ambiguous = False
            for o in options:
                if re.match(check, o):
                    if found is not None:
                        print(f"{check} is too ambiguous, try a longer abbreviation")
                        ambiguous = True
                        break

                    found = o

            if not ambiguous:
                return found
        else:
            if check in options:
                return result

    return result

def yes_no(msg, default=None, ending="?"):
    default_str = ""
    if default is not None:
        default_str = f" [{default}]"

    result = None
    while result != "y" and result != "n":
        result = input(f"{msg} [y/n]{ending}{default_str} ")
        if default != None and result == "":
            return default

    return result

def prompt_id(id_list, max_tries=10000, default=None):
    while True:
        simple_default = "n"

        if default is not None:
            if isinstance(default, int):
                simple_default = "y"
            else:
                simple_default = "n"

        simple_id = yes_no("Use simple id?", f"{simple_default}")

        if default is not None and simple_id == simple_default:
            id = default
            break

        if simple_id == "y":
            i = 0
            while i < max_tries:
                if not i in id_list:
                    break;
                i = i + 1

            if i >= max_tries:
                raise ValueError(f"For some reason max tries of {max_tries} was reached...")

            id = i
            break

        elif simple_id == "n":
            id = str(uuid.uuid4())
            break

    print (f"Id: {id}")
    return id

def get_id_list(dict_source):
    ids = []
    for s in dict_source:
        ids.append(dict_source[s].id)

    return ids

def create_source_choose_module(scrapers, default=None):
    default_str = ""
    if default is not None:
        default_str = f" [{default}]"

    while True:
        scrapers_list = []
        i = 0
        for s in scrapers:
            scrapers_list.append(s)
            print(f"{i} - {s}")
            i = i + 1

        choices = "0"
        if len(scrapers_list) > 1:
            choices = f"0-{len(scrapers_list) - 1}"

        scraper_index_str = input(f"Module [Choose from {choices}]:{default_str} ")

        if default is not None and scraper_index_str == "":
            return default

        if len(scrapers_list) == 0 and scraper_index_str == "":
            scraper_index = 0
            break

        if re.match("[0-9]+$", scraper_index_str):
            scraper_index = int(scraper_index_str)
            if scraper_index >= 0 and scraper_index < len(scrapers_list):
                return scrapers_list[scraper_index]

def edit_source(cur_sources, scrapers, file):
    source = prompt_complex_dict("Choose a source", cur_sources, "name")
    create_source(cur_sources, scrapers, file, edit_source=source)

def create_source(cur_sources, scrapers, file, edit_source=None):
    s = {}
    if edit_source is not None:
        e = edit_source
        s["id"] = e.id
        s["name"] = e.name
        s["module"] = e.module
        for p in e.module_properties:
            s[f"prop_{p}"] = e.module_properties[p]

    while True:
        s["id"] = prompt_id(get_id_list(cur_sources), default = s.get("id", None))
        s["name"] = prompt_string("Name", default=s.get("name", None))
        s["module"] = create_source_choose_module(scrapers, s.get("module", None))
        scraper = scrapers[s["module"]]
        props = scraper.get_properties()
        print("Module Properties")
        for p in props:
            s[f"prop_{p}"] = prompt_string(f"{p}", default=s.get(f"prop_{p}", None))

        print()
        print(f"Id: {s['id']}")
        print(f"Name: {s['name']}")
        print(f"Module: {s['module']}")
        print ("-----------------------------")
        for p in props:
            val = s[f"prop_{p}"]
            print(f"{p}: {val}")
#        print("}")
        print ("-----------------------------")

        confirm = yes_no("Create this source?")
        if confirm == "y":
            break

    set_props = {}
    for p in props:
        set_props[p] = s[f"prop_{p}"]

    if edit_source is None:
        source = sourcelib.Source(
            id=s["id"],
            name=s["name"],
            module=s["module"],
            module_properties=set_props
        )
    else:
        edit_source.id = s["id"]
        edit_source.name = s["name"]
        edit_source.module = s["module"]
        edit_source.module_properties = set_props
        source = edit_source

    cur_sources[s["id"]] = source
    sourcelib.save(cur_sources, file)

def create_task_add_sources(sources_dict, default=None):
    default_str = ""
    if default is not None:
        first = True
        for s in default:
            if first:
                default_str = f"[{sources_dict[s].name}"
                first = False
            else:
                default_str = f"{default_str}, {sources_dict[s].name}"

        default_str = f" {default_str}]"

    add_sources = []

    if len(sources_dict) == 0:
        log.error_print(f"No sources found. Please create a source first")
        return

    sources_list = list(sources_dict.values())
    remaining_sources = sources_list.copy()
    while len(remaining_sources) > 0:
        i = 0
        for s in remaining_sources:
            print(f"{i} - {s.name}")
            i = i + 1

        choices = "0"
        if len(remaining_sources) > 1:
            choices = f"0-{len(remaining_sources) - 1}"

        if len(add_sources) > 0:
            print("r - reset")
            print("d - done")

        if default is None or len(add_sources) > 0:
            source_index_str = input(f"Source [{choices}]: ")
        else:
            source_index_str = input(f"Source [{choices}]:{default_str} ")

        if default is not None and source_index_str == "" and len(add_sources) == 0:
            return default

        if len(remaining_sources) == 0 and source_index_str == "":
            add_sources.append(remaining_sources[source_index])
            break

        if len(add_sources):
            if source_index_str == "d":
                break
            elif source_index_str == "r":
                print ("Resetting...")
                remaining_sources = sources_list.copy()
                add_sources = []

        if re.match("[0-9]+$", source_index_str):
            source_index = int(source_index_str)

            if source_index >= 0 and source_index < len(sources_list):
                add_sources.append(remaining_sources[source_index])
                del(remaining_sources[source_index])

                confirm = yes_no("Add another?", "y")
                if confirm == "n":
                    break

    result = []
    for s in add_sources:
        result.append(s.id)

    return result

def prompt_string(msg, allow_empty=False, default=None):
    while True:
        default_str = ""
        if default is not None:
            default_str = f" [{default}]"

        result = input(f"{msg}:{default_str} ")
        if result == "":
            if default is not None:
                if allow_empty and default != "":
                    if yes_no("Set empty instead of default", default="n") == "y":
                        return ""
                    else:
                        return default
                else:
                    return default
            elif allow_empty:
                return result
        else:
            return result

def empty_list_to_empty_string(l):
    if l is None:
        return None

    if len(l) == 0:
        return ""

    return l

def prompt_complex_dict(msg, dict, display_attr, default=None):
    l = list(dict.values())

    while True:
        for i in range(len(l)):
            attr = getattr(l[i], display_attr)
            print(f"{i} - {attr}")

        s = prompt_string(msg, default=default)

        if re.match("[0-9]+$", s):
            index = int(s)
            if index >= 0 and index < len(l):
                return l[index]

def prompt_complex_list(msg, list, display_attr, default=None):
    l = list

    while True:
        for i in range(len(l)):
            attr = getattr(l[i], display_attr)
            print(f"{i} - {attr}")

        s = prompt_string(msg, default=default)

        if re.match("[0-9]+$", s):
            index = int(s)
            if index >= 0 and index < len(l):
                return l[index]

def print_title(title):
    print("--------------------------------")
    print(title)
    print("================================")

def edit_task(cur_tasks, sources, file):
    print_title("Edit Task")
    task = prompt_complex_list("Choose a task", cur_tasks, "name" )
    create_task(cur_tasks, sources, file, task)

def create_task(cur_tasks, sources, file, edit_task=None):
    print_title("Add Task")
    task_creator(cur_tasks, sources, file, edit_task=edit_task)

def task_creator(cur_tasks, sources, file, edit_task=None):
    t = {}
    if edit_task:
        e = edit_task
        old_task_name = e.name
        t["name"] = e.name
        t["freq"] = e.frequency
        t["frequ"] = e.frequency_unit
        t["sources"] = e.source_ids
        if len(e.include):
            t["include"] = ",".join(e.include)
        else:
            t["include"] = ""

        if len(e.exclude):
            t["exclude"] = ",".join(e.exclude)
        else:
            t["exclude"] = ""

    while True:
        t["name"] = prompt_string("Name", default=t.get("name", None))
        t["freq"] = prompt_num("Frequency", default=t.get("freq", 15))
        t["frequ"] = prompt_options("Frequency Unit", ["minutes", "hours"], default=t.get("frequ", "minutes"))
        t["sources"] = create_task_add_sources(sources, default=t.get("sources", None))
        t["include"] = prompt_string("Include [list seperated by commas]", allow_empty=True, default=t.get("include", None))
        t["exclude"] = prompt_string("exclude [list seperated by commas]", allow_empty=True, default=t.get("exclude", None))

        print()
        print(f"Name: {t['name']}")
        print(f"Frequency: {t['freq']} {t['frequ']}")
        print(f"Sources")
        print(f"----------------------------")
        for s in t["sources"]:
            print(f"{sources[s].name}")
        print("-----------------------------")
        print(f"Include: {t['include']}")
        print(f"Exclude: {t['exclude']}")

        """
        if edit_task is None:
            confirm_msg = "Create this task"
        else:
            confirm_msg = f"Save changes to task '{old_task_name}'"

        confirm = prompt_options(confirm_msg, ["y", "n", "quit"])
        """

        confirm = prompt_options("Choose an option", ["save", "edit", "quit"])

        if confirm == "save":
            break
        elif confirm == "edit":
            continue
        elif confirm == "quit":
            return

    if t["include"] != "":
        t["include"] = t["include"].split(",")

    if t["exclude"] != "":
        t["exclude"] = t["exclude"].split(",")

    if edit_task is None:
        task = tasklib.Task(
            name=t["name"],
            frequency=t["freq"],
            frequency_unit=t["frequ"],
            source_ids=t["sources"],
            include=t["include"],
            exclude=t["exclude"]
        )
        cur_tasks.append(task)
    else:
        e = edit_task
        e.name = t["name"]
        e.frequency = t["freq"]
        e.frequency_unit = t["frequ"]
        e.source_ids = t["sources"]
        e.include = t["include"].split(",")
        e.exclude = t["include"].split(",")

    tasklib.save(cur_tasks, file)
