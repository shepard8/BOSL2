import os
import re

EOF = 'TDEOF'
MULTIPLE_DESCRIPTIONS = 'TDMD'
MULTIPLE_USAGES = 'TDMU'

class Result:
    def __init__(self, obj, message, success, details = ""):
        self.obj = obj
        self.message = message
        self.success = success
        self.details = details

class Check:
    def __init__(self, text, test, details = lambda x : ""):
        self.text = text
        self.test = test
        self.details = details

    def check(self, obj):
        success = self.test(obj)
        message = self.text
        details = success and "" or self.details(obj)
        return Result(obj, message, success, details)

class ObjectDoc:
    def __init__(self, file, obj_type, name):
        self.file = file
        self.obj_type = obj_type
        self.name = name
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

    def add_usage(self, usage):
        if self.usage is None:
            self.usage = usage
        else:
            self.usage = MULTIPLE_USAGES

    def add_code_line(self, line):
        self.code += [line]

    def checks(self):
        return [
            Result(self, "Description is present", self.description is not None),
            Result(self, "Description is not empty", self.description is None or len(self.description) > 0),
            Result(self, "At most one description", self.description != MULTIPLE_DESCRIPTIONS),
            Result(self, "Usage is not empty", self.usage is None or len(self.usage) > 0),
            Result(self, "At most one usage block", self.usage != MULTIPLE_USAGES),
        ]

files = []
objects = []

for filename in os.listdir("."):
    if filename.endswith(".scad"):
        filepath = os.path.join(".", filename)
        files += [filepath]
        print(f"Analyzing {filepath}")
        lines = open(filepath).read().splitlines() + [EOF]
        current_obj = None
        while len(lines) > 0:
            line = lines.pop()

            # New object definition
            if re.match("// [A-Z][a-z]*( [A-Z][a-z]*)?([(][^)]*[)])?:", line):
                block_name = line[2:].split(":")[0].strip()

                if block_name in ['Section', 'Subsection', 'Constant', 'Function', 'Module', 'Module&Function']:
                    name = line.split(":")[1].split("(")[0].strip()
                    current_obj = ObjectDoc(filepath, block_name, name)
                    objects += [current_obj]
                elif current_obj is None:
                    pass
                elif block_name == 'Description':
                    description = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        description += lines[0][5:] + "\n"
                        lines.pop()
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
# - Number of functions with each type of block
