class streamFilter(object):
    def __init__(self, level):
        self._levels_dict = {50: "critical", 40: "error", 30: "warning", 20: "info", 10: "debug"}
        self._rev_levels_dict = {"critical": 50, "error": 40, "warning": 30, "info": 20, "debug": 10}
        self._level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self._rev_levels_dict[self._level.lower()]

