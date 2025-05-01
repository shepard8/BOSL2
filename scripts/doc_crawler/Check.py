from Severity import Severity

class Check:
    def __init__(self, cid, text, test, severity : Severity = Severity.needed, details = lambda x : ""):
        self.cid = cid
        self.text = text
        self.test = test
        self.severity = severity
        self.details = details
        self.successes = 0
        self.failures = 0
        self.results = {}

    def __lt__(self, other):
        return self.cid < other.cid

    def check(self, obj):
        if obj in self.results:
            return self.results[obj]

        success = self.test(obj)
        self.results[obj] = success

        if success:
            self.successes += 1
        else:
            self.failures += 1

        return success
