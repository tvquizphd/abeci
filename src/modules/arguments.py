from .defaults import Defaults, MAXIMA
from .logHandler import makeHandler

import logging
import argparse
from pathlib import Path
from datetime import datetime

FMT = argparse.ArgumentDefaultsHelpFormatter


def parseMaxima(arguments):
    maxima = enumerate(arguments.maxima)
    maxCounts = {i+1: c for i, c in maxima}
    if len(maxCounts):
        maxCounts["*"] = max(maxCounts.values())
    return maxCounts


def toLogFile(ext):
    fmt = f'%Y-%m-%dT%H%M.{ext}'
    return datetime.today().strftime(fmt)


class Text():

    tagline = "Find perfect pangrams."
    shh = "Write less, not to log file"
    debug = "Increase verbosity of logs"
    results = "Folder for output pangrams"
    effects = "Folder for intermediate steps"
    maxima = "Set max number of words for each length"
    maximumRatio = "Use at most this ratio of found words"
    maxConsonants = "Maximum consonants per word"
    maxVowels = "Maximum vowels per word"
    minWords = "Minimum words per sentence"
    maxWords = "Maximum words per sentence"


class Arguments():

    argumentKeys = {
        "formatter_class": FMT,
        "description": Text.tagline
    }
    constants = [
        Defaults.maxReps,
        Defaults.priors
    ]
    max_ = {
        "default": MAXIMA,
        "help": Text.maxima,
        "metavar": "N",
        "nargs": "*",
        "type": int
    }
    s_ = {
        "default": False,
        "help": Text.shh,
        "action": "store_true"
    }
    d_ = {
        "default": False,
        "help": Text.debug,
        "action": "store_true"
    }
    o_ = {
        "default": Defaults.oDir,
        "metavar": Defaults.oDir,
        "help": Text.results,
        "type": Path
    }
    e_ = {
        "default": Defaults.eDir,
        "metavar": Defaults.eDir,
        "help": Text.effects,
        "type": Path
    }
    r_ = {
        "default": Defaults.maxRatio,
        "help": Text.maximumRatio,
        "metavar": "R+",
        "type": float
    }
    w_ = {
        "default": Defaults.minWords,
        "help": Text.minWords,
        "metavar": "W-",
        "type": int
    }
    ww_ = {
        "default": Defaults.maxWords,
        "help": Text.maxWords,
        "metavar": "W+",
        "type": int
    }
    c_ = {
        "default": Defaults.maxConsonants,
        "help": Text.maxConsonants,
        "metavar": "C+",
        "type": int
    }
    v_ = {
        "default": Defaults.maxVowels,
        "help": Text.maxVowels,
        "metavar": "V+",
        "type": int
    }

    def __init__(self):

        dFlags = ('--debug', '-d')
        sFlags = ('--shh', '-s')
        arg_ = self.argumentKeys
        parser = argparse.ArgumentParser(**arg_)
        parser.add_argument('maxima', **self.max_)
        parser.add_argument(*dFlags, **self.d_)
        parser.add_argument(*sFlags, **self.s_)
        parser.add_argument('-o', **self.o_)
        parser.add_argument('-e', **self.e_)
        parser.add_argument('-r', **self.r_)
        parser.add_argument('-m', **self.w_)
        parser.add_argument('-w', **self.ww_)
        parser.add_argument('-c', **self.c_)
        parser.add_argument('-v', **self.v_)
        self.parser = parser

    @staticmethod
    def needed():
        cls = Arguments
        n = len(cls.constants)
        for attribute in cls.__dict__.keys():
            isOwn = attribute[:2] != "__"
            isK = attribute[-1] == "_"
            if isOwn and isK:
                n += 1
        return n

    @property
    def list(self):
        parser = self.parser
        arguments = parser.parse_args()
        maxCounts = parseMaxima(arguments)
        argumentList = [
            arguments.debug,
            arguments.o,
            arguments.e,
            arguments.shh,
            arguments.r,
            maxCounts
        ]
        for value in self.constants:
            argumentList.append(value)
        argumentList.append(arguments.m)
        argumentList.append(arguments.w)
        argumentList.append(arguments.c)
        argumentList.append(arguments.v)
        return argumentList

    def setLogging(self, debug):
        filename = Path(toLogFile("log"))
        if filename.is_file():
            already = "Refusing to overwrite"
            raise OSError(f"{already} {filename}")
        filename.touch()
        handlers = [
            makeHandler(filename),
            makeHandler()
        ]
        level = "DEBUG" if debug else "INFO"
        log_ = {
            "encoding": "utf-8",
            "handlers": handlers,
            "level": getattr(logging, level)
        }
        logging.basicConfig(**log_)
        logging.info(f"Logging to {filename}")
