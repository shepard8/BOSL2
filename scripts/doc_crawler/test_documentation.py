import os
import re
import sys
from constants import *
from Severity import Severity
from checks import checks_by_item_type

files = []
objects = []

class ObjectDoc:
    def __init__(self, file, obj_type, name):
        self.file = file
        self.obj_type = obj_type
        self.name = name
        self.synopsis = None
        self.description = None
        self.usage = None
        self.arguments = []
        self.examples = []
        self.aliases = None
        self.status = []
        self.topics = []
        self.see_also = []
        self.other_blocks = []
        self.code = []

    def add_description(self, description):
        if self.description is None:
            self.description = description
        else:
            self.description = MULTIPLE_DESCRIPTIONS

    def add_synopsis(self, synopsis):
        if self.synopsis is None:
            self.synopsis = synopsis
        else:
            self.synopsis = MULTIPLE_SYNOPSIS

    def add_usage(self, usage):
        if self.usage is None:
            self.usage = usage
        else:
            self.usage = MULTIPLE_USAGES

    def add_alias(self, alias):
        if self.aliases is None:
            self.aliases = [alias]
        else:
            self.aliases.append(alias)

    def add_code_line(self, line):
        self.code.append(line)

    def checks(self):
        return checks_by_item_type[self.obj_type]

for filename in os.listdir("."):
    if filename.endswith(".scad"):
        filepath = os.path.join(filename)
        files += [filepath]
        print(f"Analyzing {filepath}")
        lines = open(filepath).read().splitlines()
        current_obj = ObjectDoc(filepath, 'File', '')
        while len(lines) > 0:
            line = lines.pop(0)

            # New object definition
            if re.match("// [A-Z][a-z]*([ &][A-Z][a-z]*)?([(][^)]*[)])?:", line):
                block_name = line[2:].split(":")[0].strip()

                if block_name in ['Section', 'Subsection', 'Constant', 'Function', 'Module', 'Function&Module']:
                    name = line.split(":")[1].split("(")[0].strip()
                    current_obj = ObjectDoc(filepath, block_name, name)
                    objects += [current_obj]

                elif block_name == 'Synopsis':
                    synopsis = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        synopsis += lines.pop(0)[5:] + "\n"
                    current_obj.add_synopsis(synopsis)

                elif block_name == 'Description':
                    description = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        description += lines.pop(0)[5:] + "\n"
                    current_obj.add_description(description)

                elif block_name == 'Usage':
                    usage = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        usage += lines.pop(0)[5:] + "\n"
                    current_obj.add_usage(usage)

                # Aliases
                elif block_name == 'Aliases':
                    for alias in line.split(":")[1].strip().split(','):
                        current_obj.add_alias(alias.strip())

                # Arguments
                # Example
                # Status
                # Topics
                # See also
                # Other documentation block
                # Other documentation line
                else:
                    pass

            # Other comments
            elif line.startswith("//"):
                pass

            # Code
            else:
                current_obj.add_code_line(line)

if __name__ == "__main__":
    if "--file" in sys.argv:
        file = sys.argv[sys.argv.index("--file") + 1]
        files = ["./" + file]

    if "--severity" in sys.argv:
        severity = sys.argv[sys.argv.index("--severity") + 1]
        for t in checks_by_item_type:
            checks_by_item_type[t] = [c for c in checks_by_item_type[t] if str(c.severity).endswith(severity)]

    if "--check" in sys.argv:
        check = sys.argv[sys.argv.index("--check") + 1]
        for t in checks_by_item_type:
            checks_by_item_type[t] = [c for c in checks_by_item_type[t] if c.cid == check]

    hidesuccesses = False
    if "--hidesuccesses" in sys.argv:
        hidesuccesses = True

    successes = {}
    failures = {}

    for file in files:
        successes[file] = 0
        failures[file] = 0

    for obj in objects:
        if obj.file not in files:
            continue
        print(f"{obj.file} : {obj.obj_type} {obj.name}:")
        for check in obj.checks():
            if check.check(obj):
                if not hidesuccesses:
                    print(f"OK: {check.text}")
                successes[obj.file] += 1
            else:
                print(f"ERROR: Check failed: <{check.cid}> {check.text}")
                details = check.details(obj)
                if details != "":
                    print(f"Details: {details}")
                failures[obj.file] += 1
    print()

    print('Statistics by file')
    for file in files:
        print(f"Summary for {file}: {successes[file]} successes, {failures[file]} failures.")
    print()

    print('Statistics by check')
    all_checks = sorted(list(set([x for xs in checks_by_item_type.values() for x in xs])))
    print("%10s   %-15s %8s %8s %s" % ("ID", "Severity", "Success", "Failure", "Message"))
    for c in all_checks:
        print("%10s   %-15s %8s %8s %s" % (c.cid, str(c.severity).split('.')[1], c.successes, c.failures, c.text))
    print()

    print('Statistics by severity')
    summary_by_severity = {
        Severity.needed: 0,
        Severity.recommendation: 0,
        Severity.commonality: 0,
    }
    for c in all_checks:
        summary_by_severity[c.severity] += c.failures
    for (severity, count) in summary_by_severity.items():
        print(f"{severity} : {count}")
    print()

    print(f"Summary: {sum(successes.values())} successes, {sum(failures.values())} failures.")

# Statistics:
# - Number of block type with each type of item type
