from .logging import logMaxCounts

from statistics import variance
from pathlib import Path
import logging
import math


class Config:

    cList = 'bcdfghjklmnpqrstvwxz'
    vList = 'aeiouy'

    def __init__(self, shh, *args):
        (maxRatio, maxCounts, maxReps, priors) = args[:4]
        (minWords, maxWords, maxC, maxV) = args[4:]
        self.maxRatio = maxRatio
        self.maxCounts = maxCounts
        self.maxReps = maxReps
        self.priors = priors
        self.minWords = minWords
        self.maxWords = maxWords
        self.maxConsonants = maxC
        self.maxVowels = maxV
        self.output = []
        self.source = []
        self.empty = []
        self.shh = shh

    def makeFolder(self, folder):
        isDir = folder.is_dir()
        verb = "Using" if isDir else "Making"
        logFn = logging.info if isDir else logging.warning
        folder.mkdir(parents=True, exist_ok=True)
        logFn(f"{verb} {folder}")

    def makeFolders(self, parents):
        prefix = Path(self.prefix)
        for parent in parents:
            self.makeFolder(parent / prefix)
        testPath = self.toPath("*", "ext")
        logging.info(f"Paths like: {testPath}")

    def toPath(self, name, ext):
        prefix = Path(self.prefix)
        suffix = self.suffix
        text = "_".join([name, suffix])
        return prefix / Path(f"{text}.{ext}")

    def setEmpty(self, empty):
        self.empty = empty

    def addEmpty(self, line):
        self.empty.append(line)

    def addSource(self, wf):
        self.source.append(wf)

    def addOutput(self, words):
        self.output.append(" ".join(words))

    @property
    def outputLength(self):
        return len(self.output)

    @property
    def prefix(self):
        maxReps = self.maxReps
        maxRatio = self.maxRatio
        pVals = self.priors.values()
        priorValues = pVals if len(pVals) > 2 else [1, 1]
        std = math.sqrt(variance(priorValues))
        std100 = math.ceil(100 * std)
        max100 = int(100 * maxRatio)
        limitList = [k for k, v in maxReps.items() if v > 0]
        limited = "_".join(sorted(limitList))
        prefix = f"_has_{limited}" if len(limited) else ""
        return f'std{std100}_max{max100}{prefix}'

    @property
    def suffix(self):
        maxCounts = self.maxCounts
        mk = maxCounts.keys()
        if "*" not in maxCounts:
            raise ValueError(logMaxCounts(maxCounts))
        mk = sorted([k for k in mk if isinstance(k, int)])
        counts = "_".join([f"{maxCounts[k]}x{k}" for k in mk])
        suffix = f"_{counts}" if len(counts) else ""
        return f'{maxCounts["*"]}{suffix}'

    def wordRange(self):
        minWords = self.minWords
        maxWords = self.maxWords
        wordBounds = (minWords, maxWords + 1)
        return list(range(*wordBounds))

    def vowelCombos(self):
        mV = len(self.vList)
        nV = range(self.maxVowels)
        return sum([math.comb(mV, n) for n in nV])
