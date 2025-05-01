import re
from constants import *
from Severity import Severity
from Check import Check

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
