
import logging
import os
import sys
from datetime import datetime

from typing import Union, Optional
from logging import FileHandler
from logging import StreamHandler


try:
    from rkt_tool_lib.Tool import Tool, Singleton
except ImportError:
    from rkt_lib_toolkit.rkt_tool_lib.Tool import Tool, Singleton

try:
    from rkt_exception_lib.LoggerException import InvalidLogLevelError, LogIsNotDirError
except ImportError:
    from rkt_lib_toolkit.rkt_exception_lib.LoggerException import InvalidLogLevelError, LogIsNotDirError

try:
    from rkt_logger_lib.Logger import Logger
except ImportError:
    from rkt_lib_toolkit.rkt_logger_lib.Filters.MyFilters import streamFilter


class Logger(metaclass=Singleton):
    """
    Custom logger lib

    """
    __slots__ = ["_me", "_tool", "_loggers", "_log_file", "_formatter", "_levels_dict", "_Logger_formatter",
                 "_log_dir_path", "_rev_levels_dict"
                 ]

    def __init__(self, caller_class: str, log_dir_path: str = "log") -> None:
        self._me = self.__class__.__name__
        self._tool = Tool()
        self._loggers = {}

        self._log_dir_path = self._tool.get_dir(log_dir_path)

        if not self._log_dir_path:
            log_dir_path = f"{self._tool.formatted_from_os(self._tool.get_cwd())}{log_dir_path}"
            if not os.path.exists(log_dir_path):
                os.mkdir(log_dir_path)
            elif not os.path.isdir(log_dir_path):
                raise LogIsNotDirError("\"log\" isn't a directory")
            self._log_dir_path = self._tool.get_dir(log_dir_path)

        self._log_file = f'{self._log_dir_path}output_{datetime.today().date()}.log'
        self._formatter = logging.Formatter(f'%(asctime)s :: [{caller_class}] :: %(levelname)s :: %(message)s',
                                            "%d/%m/%Y %H:%M:%S")
        self._Logger_formatter = logging.Formatter(f'%(asctime)s :: [Logger] :: %(levelname)s :: %(message)s',
                                                   "%d/%m/%Y %H:%M:%S")
        self._levels_dict = {}
        self._rev_levels_dict = {}
        self._init()

    def _init(self) -> None:
        """
        Check and correct (if necessary) mandatory folders or quit in case of inability to correct
        Set private "_levels_dict" var :
            CRITICAL 50   The whole program is going to hell.
            ERROR    40   Something went wrong.
            WARNING  30   To warn that something deserves attention: triggering a particular mode,
                          detecting a rare situation, an optional lib can be installed.
            INFO     20   To inform about the running of the program. For example: “Starting CSV parsing”
            DEBUG    10   To dump information when you are debugging. Like knowing what's in that fucking dictionary.

        REMEMBER :
            Each time you send a message, the logger (and each handler) will compare the lvl of the message with its own
            if the level of the message is lower than his, he ignores it, otherwise he writes it.
        """

        self._levels_dict = {50: "CRITICAL", 40: "ERROR", 30: "WARNING", 20: "INFO", 10: "DEBUG"}
        self._rev_levels_dict = {"critical": 50, "error": 40, "warning": 30, "info": 20, "debug": 10}

        self.set_logger(caller_class=self._me, level="DEBUG")

    def set_logger(self, caller_class: str, out_file: Optional[str] = "", output: str = "both",
                   level: Union[int, str] = "INFO") -> None:
        """
        Set and store new Logger

        :param out_file:
        :param str caller_class: name of class who want write log use to get Logger of it
        :param str output: output type
        :param str or int level:
        :return: None
        """
        if out_file:
            self._log_file = f'{self._log_dir_path}{out_file}_{datetime.today().date()}.log'

        if isinstance(level, int):
            level = self._levels_dict[level]

        handlers = []
        if caller_class != self._me:
            self.add(level="info", caller=self._me, message=f"Create logger for '{caller_class}'")

        if output in ["stream", "both"]:
            if (isinstance(level, str) and self._rev_levels_dict[level.lower()] <= self._rev_levels_dict["warning"]) \
                    or (isinstance(level, int) and level <= self._rev_levels_dict["warning"]):
                stream_stdout = StreamHandler(stream=sys.stdout)
                stream_stdout.setLevel(level)
                stream_stdout.addFilter(streamFilter("WARNING"))
                handlers.append(stream_stdout)

            stream_stderr = StreamHandler(stream=sys.stderr)
            stream_stderr.setLevel("ERROR")
            stream_stderr.addFilter(streamFilter("CRITICAL"))

            handlers.append(stream_stderr)

        if output in ["file", "both"]:
            handlers.append(FileHandler(filename=self._log_file, mode="a"))

        self._add_handlers(caller_class=caller_class, handlers=handlers, level=level)

    def _add_handlers(self, caller_class: str, handlers: list, level: str = "INFO") -> None:
        """
        Generic method to add message with a log level

        :param str caller_class: name of class who want write log use to get Logger of it
        :param str level: log level
        :param list handlers: list of handker need to be add in the logger
        :return:
        """
        log = logging.getLogger(name=caller_class)
        log.setLevel(level=getattr(logging, f'{level}'))
        self._formatter = logging.Formatter(f'%(asctime)s :: [{caller_class}] :: %(levelname)s :: %(message)s',
                                            "%d/%m/%Y %H:%M:%S")

        for handler in handlers:
            handler.setFormatter(fmt=self._formatter if caller_class != "Logger" else self._Logger_formatter)
            log.addHandler(hdlr=handler)
            if caller_class != self._me:
                self.add(level="info", caller=self._me,
                         message=f"add '{type(handler).__name__}' in '{caller_class}' logger")
        self._loggers[caller_class] = log

    def add(self, caller: str, message: str, level: Union[int, str] = 20) -> None:
        """
        Generic method to add message with a log level

        :rtype: object
        :param str caller: name of class who want write log use to get Logger of it
        :param str level: log level
        :param str message: message to log
        :return:
        """
        if isinstance(level, int):
            if level not in self._levels_dict.keys():
                self.add(level=50, caller=self._me,
                         message=f"You try to add a message in the logger with non existing value of log level")
                raise InvalidLogLevelError(f"Log level {level} doesn't exist")
            level = self._levels_dict[level]
        getattr(self._loggers[caller], f'{level.lower()}')(message)

    def get_logger_file(self, logger_name: str) -> Optional[str]:
        try:
            for handler in self._loggers[logger_name].handlers:
                if isinstance(handler, FileHandler):
                    return handler.baseFilename
        except KeyError:
            return None

    def check_logger_exist(self, logger_name: str) -> bool:
        if logger_name not in list(self._loggers.keys()):
            return False

        return True
