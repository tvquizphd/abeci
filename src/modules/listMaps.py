from .maps import mapFunction
from .maps import getVowelKey
from .logging import CutLogger
from .logging import DeltaLogger
from .logging import logMaxCounts

from bisect import insort
import math


def getPriors(priors):
    def getPrior(char):
        default = 1 / len(priors)
        return priors.get(char, default)
    return getPrior


class Word():

    def __init__(self, word, frequency, letters, priors):
        self.word = word
        self.letters = letters
        pList = list(map(getPriors(priors), letters))
        self.score = frequency / math.prod(pList)


def isGoodWord(letters, config):
    maxConsonants = config.maxConsonants
    maxVowels = config.maxVowels
    vList = config.vList
    vCount = sum(v in letters for v in vList)
    cCount = len(letters) - vCount
    if cCount > maxConsonants or vCount > maxVowels:
        return False
    return True


def updateWords(keyMap, key, w):
    noted = keyMap.get(key, [])
    score = w.score
    word = w.word
    try:
        copyIndex = next(i for i, v in enumerate(noted) if v.word == word)
        noted[copyIndex].score = max(noted[copyIndex].score, score)
    except StopIteration:
        insort(noted, w, key=lambda v: v.score)
    return noted


def isOver(keyCount, letters, config):
    nLetters = len(letters)
    maxCounts = config.maxCounts
    totalWords = maxCounts.get(nLetters, maxCounts['*'])
    keyMax = totalWords / config.vowelCombos()
    return keyCount > keyMax


def hashWord(word):
    letterList = [c for c in set(word) if c.isalpha()]
    return ''.join(sorted(letterList))


def listMaps(loop, typos, config):
    kWords = {}
    kTotals = {}
    shh = config.shh
    dLogger = DeltaLogger(shh)
    priors = config.priors
    maxRatio = config.maxRatio
    maxCounts = config.maxCounts
    if "*" not in maxCounts:
        raise ValueError(logMaxCounts(maxCounts))

    for (word, frequency) in loop:
        letters = hashWord(word)
        # Repeat letters are impossible
        if len(word) > len(letters):
            continue
        config.addSource([word, frequency])
        # Ensure word meets configured requirements
        if not isGoodWord(letters, config):
            continue
        if word in typos:
            continue
        # Insert word sorted by score
        key = getVowelKey(letters, config.vList)
        w = Word(word, frequency, letters, priors)
        kWords[key] = updateWords(kWords, key, w)
        kTotals[key] = kTotals.get(key, 0) + 1
        # Cut lowest-scoring words
        oArgs = (len(kWords[key]), letters, config)
        over = isOver(*oArgs)
        logWord = word
        if over:
            logWord = kWords[key].pop(0).word
        # Logging
        dLogger.log(over, logWord, word)

    wsMap = {}
    cutLogger = CutLogger(shh)

    # Higher frequencies first
    for key, wList in kWords.items():
        total = kTotals.get(key, 0)
        maxAllowed = max(int(total*maxRatio), 1)
        cutLogger.add(wList, maxAllowed)
        # Allow at most fixed ratio of words
        for w in wList[::-1][:maxAllowed]:
            wValue = [w.word, w.score]
            letterList = wsMap.get(w.letters, [])
            wsMap[w.letters] = letterList + [wValue]

    cutLogger.log(maxRatio)

    toMaps = mapFunction(config)
    return toMaps(wsMap)
