import os
import re
from constants import *
from checks import checks_by_item_type

class ArgumentDoc:
    def __init__(self, name, description, section):
        self.name = name
        self.description = description
        self.section = section

class ObjectDoc:
    def __init__(self, file, obj_type, name):
        self.file = file
        self.obj_type = obj_type
        self.name = name
        self.synopsis = None
        self.description = None
        self.usages = []
        self.arguments = []
        self.examples = []
        self.aliases = None
        self.statuses = []
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
        self.usages.append(usage)

    def add_alias(self, alias):
        if self.aliases is None:
            self.aliases = [alias]
        else:
            self.aliases.append(alias)

    def add_status(self, status):
        self.statuses.append(status)

    def add_topic(self, topic):
        self.topics.append(topic)

    def add_argument(self, argument):
        self.arguments.append(argument)

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

                def read_content():
                    block_content = line.split(":", 1)[1]
                    while lines[0].startswith("//   "):
                        block_content += "\n" + lines.pop(0)[5:]
                    return block_content

                if block_name in ['Section', 'Subsection', 'Constant', 'Function', 'Module', 'Function&Module']:
                    name = read_content().split("(")[0].strip()
                    current_obj = ObjectDoc(filepath, block_name, name)
                    objects.append(current_obj)

                elif block_name == 'Synopsis':
                    current_obj.add_synopsis(read_content())

                elif block_name == 'Description':
                    current_obj.add_description(read_content())

                elif block_name == 'Usage':
                    current_obj.add_usage(read_content())

                elif block_name == 'Aliases':
                    for alias in read_content().split(','):
                        current_obj.add_alias(alias.strip())

                elif block_name == 'Status':
                    current_obj.add_status(read_content())

                elif block_name == 'Topics':
                    for topic in read_content().replace('\n', ',').split(','):
                        current_obj.add_topic(topic)

                # Arguments
                elif block_name == 'Arguments':
                    arg_section = 1
                    while lines[0].startswith("//   "):
                        arg_line = lines.pop(0)[5:].strip()
                        if arg_line == "---":
                            arg_section += 1
                            continue
                        if '=' in arg_line:
                            arg_name, arg_desc = arg_line.split('=', 1)
                        else:
                            arg_name = arg_line
                            arg_desc = ""
                        current_obj.add_argument(ArgumentDoc(arg_name.strip(), arg_desc.strip(), arg_section))

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