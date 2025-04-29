import os
import re
from enum import Enum

EOF = 'TDEOF'
MULTIPLE_DESCRIPTIONS = 'TDMD'
MULTIPLE_USAGES = 'TDMU'
MULTIPLE_SYNOPSIS = 'TDMS'

class Severity(Enum):
    commonality = 0
    recommendation = 1
    needed = 2

class Result:
    def __init__(self, obj, message, success, severity : Severity = Severity.needed, details = ""):
        self.obj = obj
        self.message = message
        self.success = success
        self.severity = severity
        self.details = details

class Check:
    def __init__(self, text, test, severity : Severity = Severity.needed, details = lambda x : ""):
        self.text = text
        self.test = test
        self.details = details
        self.successes = 0
        self.failures = 0

    def check(self, obj):
        success = self.test(obj)
        message = self.text
        details = success and "" or self.details(obj)

        if success:
            self.successes += 1
        else:
            self.failures += 1

        return Result(obj, message, success, details)

description_checks = [
    Check("Description is present", lambda o: o.description is not None),
    Check("Description is not empty", lambda o: o.description is None or len(o.description) > 0),
    Check("At most one description", lambda o: o.description != MULTIPLE_DESCRIPTIONS),
]

synopsis_checks = [
    Check("Synopsis is present", lambda o: o.synopsis is not None, Severity.commonality),
    Check("Synopsis is not empty", lambda o: o.synopsis is None or len(o.synopsis) > 0),
    Check("At most one synopsis", lambda o: o.synopsis != MULTIPLE_SYNOPSIS),
    Check("Synopsis is single line", lambda o: o.synopsis is None or len(o.synopsis.strip().splitlines()) == 1)
]

usage_checks = [
    Check("Usage is present", lambda o: o.usage is not None, Severity.recommendation),
    Check("Usage is not empty", lambda o: o.usage is None or len(o.usage) > 0),
    Check("At most one usage block", lambda o: o.usage != MULTIPLE_USAGES),
]

checks_by_item_type = {
    "File": [],
    "Constant": description_checks + synopsis_checks,
    "Function": description_checks + synopsis_checks + usage_checks,
    "Module": description_checks + synopsis_checks + usage_checks,
    "Module&Function": description_checks + synopsis_checks + usage_checks,
    "Section": [],
    "Subsection": [],
}

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
        self.aliases = []
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

    def add_code_line(self, line):
        self.code += [line]

    def checks(self):
        return [c.check(self) for c in checks_by_item_type[self.obj_type]]

files = []
objects = []

for filename in os.listdir("."):
    if filename.endswith(".scad"):
        filepath = os.path.join(".", filename)
        files += [filepath]
        print(f"Analyzing {filepath}")
        lines = open(filepath).read().splitlines() + [EOF]
        current_obj = ObjectDoc(filepath, 'File', '')
        while len(lines) > 0:
            line = lines.pop()

            # New object definition
            if re.match("// [A-Z][a-z]*( [A-Z][a-z]*)?([(][^)]*[)])?:", line):
                block_name = line[2:].split(":")[0].strip()

                if block_name in ['Section', 'Subsection', 'Constant', 'Function', 'Module', 'Module&Function']:
                    name = line.split(":")[1].split("(")[0].strip()
                    current_obj = ObjectDoc(filepath, block_name, name)
                    objects += [current_obj]

                elif block_name == 'Synopsis':
                    synopsis = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        synopsis += lines.pop()[5:] + "\n"
                    current_obj.add_synopsis(synopsis)

                elif block_name == 'Description':
                    description = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        description += lines.pop()[5:] + "\n"
                    current_obj.add_description(description)



                # Usage
                # Arguments
                # Example
                # Alias
                # Status
                # Topics
                # See also
                # Other documentation block
                # Other documentation line
                else:
                    pass
            elif line.startswith("//"):
                pass
            # Code
            else:
                if current_obj is None:
                    pass
                else:
                    current_obj.add_code_line(line)

if __name__ == "__main__":
    successes = {}
    failures = {}

    for file in files:
        successes[file] = 0
        failures[file] = 0

    for obj in objects:
        print(f"{obj.file} : {obj.obj_type} {obj.name}:")
        for check in obj.checks():
            if check.success:
                print(f"OK: {check.message}")
                successes[obj.file] += 1
            else:
                print(f"ERROR: Check failed: <{check.message}>")
                if check.details != "":
                    print(f"Details: {check.details}")
                failures[obj.file] += 1
        print(f"Summary for ")

    for file in files:
        print(f"Summary for {file}: {successes[file]} successes, {failures[file]} failures.")

    print(f"Summary: {sum(successes.values())} successes, {sum(failures.values())} failures.")

# Statistics:
# - By file
# - By Check
# - By Severity
# - Number of block type with each type of item type
