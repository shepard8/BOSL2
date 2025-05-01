import sys
from Severity import Severity
from parse_doc import *

if __name__ == "__main__":
    files = list_files(".")
    objects = parse_doc(files)

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
