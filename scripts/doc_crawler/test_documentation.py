import os
import re
import sys
from Severity import Severity
from Check import Check

MULTIPLE_DESCRIPTIONS = 'TDMD'
MULTIPLE_USAGES = 'TDMU'
MULTIPLE_SYNOPSIS = 'TDMS'

files = []
objects = []

aliases_constant_checks = [
    Check("ConAlias.1", "Constant aliases are defined in code", lambda o: o.aliases is None or set([f"{a}={o.name};" for a in o.aliases]).issubset({x.replace(' ', '') for x in o.code})),
    Check("ConAlias.2", "Non-empty constant aliases block", lambda o: o.aliases is None or len(o.aliases) > 0),
    Check("ConAlias.3", "No duplicate aliases for constants", lambda o: o.aliases is None or len(o.aliases) == len(set(o.aliases))),
]

def alias_defined(kw, code, name, alias):
    alias = alias.replace("()", "").strip()
    definition_start = [i for (i, x) in enumerate(code) if x.startswith(kw + " ") and x.replace(" ", "").startswith(kw + name + "(")][0]
    definition = "".join(code[definition_start:]).replace(" ", "").split(")")[0].replace(kw + name + "(", "")
    try:
        alias_start = [i for (i, x) in enumerate(code) if x.startswith(kw + " ") and x.replace(" ", "").startswith(kw + alias + "(")][0]
        alias_definition = "".join(code[alias_start:]).replace(" ", "").split(")")[0].replace(kw + alias + "(", "")
        return definition == alias_definition
    except IndexError:
        return False

aliases_fun_checks = [
    Check("FunAlias.1", "Function aliases are defined, with same arguments", lambda o: o.aliases is None or False not in [alias_defined("function", o.code, o.name, alias) for alias in o.aliases]),
    Check("FunAlias.2", "Non-empty function aliases block", lambda o: o.aliases is None or len(o.aliases) > 0),
    Check("FunAlias.3", "No duplicate aliases for functions", lambda o: o.aliases is None or len(o.aliases) == len(set(o.aliases))),
]

aliases_mod_checks = [
    Check("ModAlias.1", "Module aliases are defined, with same arguments", lambda o: o.aliases is None or False not in [alias_defined("module", o.code, o.name, alias) for alias in o.aliases]),
    Check("ModAlias.2", "Non-empty module aliases block", lambda o: o.aliases is None or len(o.aliases) > 0),
    Check("ModAlias.3", "No duplicate aliases for modules", lambda o: o.aliases is None or len(o.aliases) == len(set(o.aliases))),
]

aliases_funmod_checks = [
    Check("FMAlias.1", "Function&Module aliases are defined, with same arguments", lambda o: o.aliases is None or False not in [alias_defined("function", o.code, o.name, alias) for alias in o.aliases] and False not in [alias_defined("module", o.code, o.name, alias) for alias in o.aliases]),
    Check("FMAlias.2", "Non-empty function&module aliases block", lambda o: o.aliases is None or len(o.aliases) > 0),
    Check("FMAlias.3", "No duplicate aliases for function&modules", lambda o: o.aliases is None or len(o.aliases) == len(set(o.aliases))),
]

description_checks = [
    Check("Desc.1", "Description is present", lambda o: o.description is not None),
    Check("Desc.2", "Description is not empty", lambda o: o.description is None or len(o.description) > 0),
    Check("Desc.3", "At most one description", lambda o: o.description != MULTIPLE_DESCRIPTIONS),
]

synopsis_checks = [
    Check("Syn.1", "Synopsis is present", lambda o: o.synopsis is not None, Severity.commonality),
    Check("Syn.2", "Synopsis is not empty", lambda o: o.synopsis is None or len(o.synopsis) > 0),
    Check("Syn.3", "At most one synopsis", lambda o: o.synopsis != MULTIPLE_SYNOPSIS),
    Check("Syn.4", "Synopsis is single line", lambda o: o.synopsis is None or len(o.synopsis.strip().splitlines()) == 1)
]

usage_checks = [
    Check("Usage.1", "Usage is present", lambda o: o.usage is not None, Severity.recommendation),
    Check("Usage.2", "Usage is not empty", lambda o: o.usage is None or len(o.usage) > 0),
]

code_constant_checks = [
    Check("ConCode.1", "Constant is defined after documentation", lambda o: len(o.code) > 0),
    Check("ConCode.2", "Correct constant is defined (`NAME = `)", lambda o: re.match(f"^{o.name}[ ]*=", " ".join(o.code).strip()), Severity.needed, lambda o: '\n'.join(o.code)),
]

checks_by_item_type = {
    "File": [],
    "Constant": description_checks + synopsis_checks + code_constant_checks + aliases_constant_checks,
    "Function": description_checks + synopsis_checks + usage_checks + aliases_fun_checks,
    "Module": description_checks + synopsis_checks + usage_checks + aliases_mod_checks,
    "Function&Module": description_checks + synopsis_checks + usage_checks + aliases_funmod_checks,
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
