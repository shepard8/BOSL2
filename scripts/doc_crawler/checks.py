import re
from constants import *
from Severity import Severity
from Check import Check

def todo():
    return False

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
    Check("Usage.1", "At least one Usage block", lambda o: len(o.usages) > 0, Severity.recommendation),
    Check("Usage.2", "Usage is not empty", lambda o: all([len(u) > 0 for u in o.usages])),
    Check("Usage.3", "Usage shows positional arguments", lambda o: todo()),
    Check("Usage.3", "Usage shows named arguments", lambda o: todo()),
]

status_checks = [
    Check("Status.1", "Status is not empty", lambda o: len([s for s in o.statuses if len(s) == 0]) == 0),
    Check("Status.2", "Status is DEPRECATED", lambda o: len([s for s in o.statuses if not s.startswith("DEPRECATED")]) == 0),
    Check("Status.2", "Status DEPRECATED contains information (e.g., about alternative)", lambda o: len([s for s in o.statuses if s.startswith("DEPRECATED") and len(s) <= len("DEPRECATED")]) == 0, Severity.commonality),
]

topic_checks = [
    Check("Topics.1", "Topics have less than 3 words", lambda o: len([t for t in o.topics if len(t.split(' ')) > 3]) == 0),
]

argument_checks = [
    Check("Arg.1", "Arguments match [a-z_]+", lambda o: all([re.match("^[a-z_]+$", a.name) for a in o.arguments])),
    Check("Arg.2", "Description is not empty", lambda o: all([len(a.description) > 0 for a in o.arguments])),
    Check("Arg.3", "Description ends with a dot", lambda o: all([a.description.endswith(".") for a in o.arguments]), Severity.commonality),
    Check("Arg.4", "There are at most two sections", lambda o: all([a.section < 3 for a in o.arguments])),
]

code_constant_checks = [
    Check("ConCode.1", "Constant is defined after documentation", lambda o: len(o.code) > 0),
    Check("ConCode.2", "Correct constant is defined (`NAME = `)", lambda o: re.match(f"^{o.name}[ ]*=", " ".join(o.code).strip()), Severity.needed, lambda o: '\n'.join(o.code)),
]

code_module_checks = [
    Check("ModCode.1", "There is a module in code matching arguments block", lambda o: todo()),
]

code_function_checks = [
    Check("FunCode.1", "There is a function in code matching arguments block", lambda o: todo()),
]

common_checks = description_checks + synopsis_checks + status_checks + argument_checks
checks_by_item_type = {
    "File": [],
    "Constant": common_checks + code_constant_checks + aliases_constant_checks,
    "Function": common_checks + usage_checks + aliases_fun_checks + code_function_checks,
    "Module": common_checks + usage_checks + aliases_mod_checks + code_module_checks,
    "Function&Module": common_checks + usage_checks + aliases_funmod_checks + code_function_checks + code_module_checks,
    "Section": [],
    "Subsection": [],
}
