from .writePatterns import writePatterns
from .readFromCache import readFromCache
from .readFromCache import writeLines
from .readFromCache import readLines

from google_ngram_downloader import readline_google_store
from statistics import variance
from bisect import insort
from pathlib import Path
import unidecode
import signal
import math
import yaml
import sys


def updateWords(noted, wf):
    word = wf["w"]
    freq = wf["f"]
    try:
        copyIndex = next(i for i, v in enumerate(noted) if v["w"] == word)
        noted[copyIndex]["f"] = max(noted[copyIndex]["f"], freq)
    except StopIteration:
        insort(noted, wf, key=lambda v: v["f"])
    return noted


def isWordOkay(word):
    for part in word.split("_"):
        isText = all([c.isalpha() for c in part])
        isReal = any([not c.isupper() for c in part])
        if not isText or not isReal:
            return False
    return True


def readWordRecords():
    lists = readline_google_store(ngram_len=1)
    for fname, url, records in lists:
        filename = fname.split('.')[0]
        suffix = filename.split('-')[-1]
        if len(suffix) > 1 or not suffix[0].isalpha():
            continue
        for record in records:
            if record.year == 2008:
                word = unidecode.unidecode(record.ngram)
                if isWordOkay(word):
                    frequency = record.match_count
                    yield (word.lower(), frequency)


def isGoodWord(word, letters, maxConsonants, maxVowels):
    if len(word) > len(letters):
        return False
    vCount = sum(v in letters for v in "aeiouy")
    cCount = len(letters) - vCount
    if cCount > maxConsonants or vCount > maxVowels:
        return False
    return True


def weighFrequency(chars, baseline, frequency):
    prior = math.prod([baseline.get(c, 1) for c in chars])
    return frequency / prior


def countLetterSets(minFreq, maxConsonants, maxVowels, maxCounts, cList, baseline):
    # Ignore any word with <8192 (2**13) frequency
    wordsByKey = {}
    lastWords = (" ", " ")
    lastFirstLetter = " "
    deltas = {"+": [], "-": []}

    for (word, frequency) in readWordRecords():
        letters = hashWord(word)
        key = getVowelKey(letters)
        maxKey = str(len(letters))
        keyMax = maxCounts.get(maxKey, maxCounts['*'])
        freq = weighFrequency(letters, baseline, frequency)
        if freq < minFreq:
            continue
        if not isGoodWord(word, letters, maxConsonants, maxVowels):
            continue
        wf = {"w": word, "f": freq, "l": letters}
        keyWords = wordsByKey.get(key, [])
        # Deduplicate with maximum frequency
        wordsByKey[key] = updateWords(keyWords, wf)
        keyCount = len(wordsByKey[key])
        excess = keyCount > keyMax
        logWord = word
        symbol = "+"
        logLen = 500
        if excess:
            logWord = wordsByKey[key].pop(0)["w"]
            symbol = "-"
        # logging
        deltas[symbol].append(logWord)
        if len(deltas[symbol]) >= logLen:
            deltas[symbol] = []
            logTxt = f"{symbol}{logWord}"
            print(logTxt, end=",", flush=True)
        f0 = lastWords[0][0]
        f1 = lastWords[1][0]
        f2 = word[0][0]
        if f0 != f1 and f1 == f2 and f2 != lastFirstLetter:
            lastFirstLetter = f2
            print(f"\n{f2}:")
        # Track last two words
        lastWords = (lastWords[1], word)

    wordsByLetter = {}
    # Higher frequencies prepended
    for keyWords in wordsByKey.values():
        for wf in keyWords:
            letterList = wordsByLetter.get(wf["l"], [])
            wordsByLetter[wf["l"]] = [wf["w"], *letterList]

    return wordsByLetter


def writeWordFile(wordFile, minFreq, maxConsonants, maxVowels, maxCounts, cList, baseline):

    wordsByLetter = countLetterSets(minFreq, maxConsonants, maxVowels, maxCounts, cList, baseline)

    print()
    print(f'writing {wordFile}...')
    with open(wordFile, "w") as wf:
        yaml.dump(wordsByLetter, wf)

    print('written.')


def getVowelKey(s):
    uniq = set(s)
    aeiouy = "aeiouy"
    vow = [v for v in uniq if v in aeiouy]
    cNum = len(uniq) - len(vow)
    vowX = vow if len(vow) else "x"
    return "".join([str(cNum)] + sorted(vowX))


def toLetterMap(wordMap):
    letterMap = {'': []}
    for combo in wordMap.keys():
        key = getVowelKey(combo)
        combos = letterMap.get(key, [])
        letterMap[key] = [*combos, combo]
    return letterMap


def flattenList(tree):
    if len(tree) == 0:
        return tree
    if isinstance(tree[0], list):
        return flattenList(tree[0]) + flattenList(tree[1:])
    return tree[:1] + flattenList(tree[1:])


def noModification(v):
    return v


def toHash(list):
    return ''.join(sorted(list))


def hashWord(word):
    letterList = [c for c in set(word) if c.isalpha()]
    return toHash(letterList)


class FileHandler:

    cList = 'bcdfghjklmnpqrstvwxz'
    maxConsonants = 6
    maxVowels = 2

    def __init__(self, eDir, oDir, minFreq, maxCounts, maxReps, baseline):
        self.output = []
        cList = self.cList
        self.emptyLines = []
        maxVowels = self.maxVowels
        maxConsonants = self.maxConsonants
        suffix = f'{maxCounts["*"]}xx'
        for k in sorted(maxCounts.keys()):
            if k == "*":
                continue
            suffix = f'{suffix}_{maxCounts[k]}x{k}'
        prefix = ""
        for k in sorted(maxReps.keys()):
            if maxReps[k] == 0:
                prefix = f"_no{k}{prefix}"
        baseVar = 0
        if len(baseline) >= 2:
            baseVariance = variance(baseline.values())
            baseVar = int(100 * baseVariance)
        prefix = f'var{baseVar}_over{minFreq}{prefix}'

        self.patternFile = eDir / Path(f"{prefix}_pattern_{suffix}.yaml")
        self.wordFile = eDir / Path(f"{prefix}_wordMap_{suffix}.yaml")
        self.emptyFile = eDir / Path(f"{prefix}_empty_{suffix}.txt")
        self.outFile = oDir / Path(f"{prefix}_pangrams_{suffix}.txt")
        print(f"prefix: {prefix}, suffix: {suffix}")

        if not self.wordFile.is_file():
            writeWordFile(self.wordFile, minFreq, maxConsonants, maxVowels, maxCounts, cList, baseline)

        self.wordMap = readFromCache(self.wordFile, noModification)
        self.letterMap = toLetterMap(self.wordMap)

        if not self.patternFile.is_file():
            writePatterns(self.patternFile, self.letterMap, maxReps, maxConsonants, maxVowels)

        # Register ctrl-C
        signal.signal(signal.SIGINT, self.exit)

    def finish(self):
        outCount = len(self.output)
        emptyCount = len(self.emptyLines)
        writeLines(self.emptyFile, self.emptyLines)
        writeLines(self.outFile, self.output)
        print(f'Saved {outCount} perfect pangram sets to {self.outFile}')
        print(f'Saved {emptyCount} unused patterns to {self.emptyFile}')

    def exit(self, s, f):
        try:
            self.finish()
        except (BrokenPipeError, IOError):
            pass
        sys.exit(0)

    def readLeafList(self):
        knownEmpty = readLines(self.emptyFile)
        inList = readFromCache(self.patternFile, flattenList)
        return [i for i in inList if i not in knownEmpty] + ['']
