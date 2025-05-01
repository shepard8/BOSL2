import os
import re
from constants import *
from checks import checks_by_item_type

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

def list_files(dir):
    files = []
    for filename in os.listdir(dir):
        if filename.endswith(".scad"):
            filepath = os.path.join(filename)
            files += [filepath]
    return files

def parse_doc(files):
    objects = []

    for filepath in files:
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

                # Status
                elif block_name == 'Status':
                    status = line.split(":")[1].strip() + "\n"
                    while lines[0].startswith("//   "):
                        status += lines.pop(0)[5:] + "\n"
                    current_obj.add_status(status)

                # Arguments
                # Example
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

    return objects