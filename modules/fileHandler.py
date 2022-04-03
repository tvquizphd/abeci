from .writePatterns import writePossibleFile
from .readFromCache import readFromCache
from .readFromCache import writeLines
from .readFromCache import readLines

from google_ngram_downloader import readline_google_store
from bisect import insort
from pathlib import Path
import unidecode
import signal
import yaml
import sys


def countLength(maxWords, shortMaxima, bigMax):
    smallLength = len(shortMaxima)
    bigMaxs = [bigMax] * (maxWords - smallLength)
    lengthCounts = [0] + shortMaxima + bigMaxs
    someCounts = lengthCounts[1:2+smallLength]
    lengthKey = "_".join(map(str, someCounts))
    return lengthKey, lengthCounts


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
            print(f'{filename}')
            continue
        for record in records:
            if record.year == 2008:
                word = unidecode.unidecode(record.ngram)
                if isWordOkay(word):
                    freq = record.match_count
                    yield (word.lower(), freq)


def isGoodWord(word, letters, v1, v2, maxConsonants):
    if len(word) > len(letters):
        return False
    eCount = 1 if "e" in letters else 0
    v1Count = sum(v in letters for v in v1)
    v2Count = sum(v in letters for v in v2)
    vCount = sum([eCount, v1Count, v2Count])
    cCount = len(letters) - vCount
    if eCount > 0 and vCount > 1:
        return False
    if v1Count > 1 or vCount > 2:
        return False
    if cCount > maxConsonants:
        return False
    return True


def countLetterSets(minPow, maxConsonants, lengthCounts, cList, v1, v2):
    # Ignore any word with <8192 (2**13) frequency
    minimum = int(2**minPow)
    wordsByLength = {}
    firstLetter = " "

    for (word, freq) in readWordRecords():
        letters = hashWord(word)
        length = len(letters)
        if length >= len(lengthCounts) or freq < minimum:
            continue
        if not isGoodWord(word, letters, v1, v2, maxConsonants):
            continue
        wf = {"w": word, "f": freq, "l": letters}
        sameLength = wordsByLength.get(length, [])
        # Deduplicate with maximum frequency
        lengthMax = lengthCounts[length]
        wordsByLength[length] = updateWords(sameLength, wf)
        wordLength = len(wordsByLength[length])
        # Remove excess words
        if wordLength > lengthMax:
            lostWord = wordsByLength[length].pop(0)["w"]
            print(f"-{lostWord}", end="", flush=True)
        elif wordLength % max(lengthMax // 100,    1) == 0:
            print(f"+{length}", end="", flush=True)
        # Update and log first letter
        if firstLetter != word[0]:
            firstLetter = (word+" ")[0]
            print(f"\n{word[0]}:")

    wordsByLetter = {}
    # Higher frequencies prepended
    for sameLength in wordsByLength.values():
        for wf in sameLength:
            letterList = wordsByLetter.get(wf["l"], [])
            wordsByLetter[wf["l"]] = [wf["w"], *letterList]

    return wordsByLetter


def writeWordFile(wordFile, minPow, maxConsonants, lengthCounts, cList, v1, v2):

    wordsByLetter = countLetterSets(minPow, maxConsonants, lengthCounts, cList, v1, v2)

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


def pickFirstWord(wordLists):
    return {k: w[0] for k, w in wordLists.items()}


def toHash(list):
    return ''.join(sorted(list))


def hashWord(word):
    letterList = [c for c in set(word) if c.isalpha()]
    return toHash(letterList)


class FileHandler:

    cList = 'bcdfghjklmnpqrstvwxz'
    maxConsonants = 6
    minPow = 8
    v1 = "aio"
    v2 = "yu"

    def __init__(self, eDir, oDir, maxima):
        v1 = self.v1
        v2 = self.v2
        self.output = []
        cList = self.cList
        minPow = self.minPow
        self.emptyLines = []
        [*shortMaxima, bigMax] = maxima
        maxConsonants = self.maxConsonants
        vCounts = [len(v) for v in (v1, v2)]
        maxWords = maxConsonants + max(vCounts)
        lengthKey, lengthCounts = countLength(maxWords, shortMaxima, bigMax)

        self.possibleFile = eDir / Path(f"{lengthKey}_possible.yaml")
        self.wordFile = eDir / Path(f"{lengthKey}_wordMap.yaml")
        self.emptyFile = eDir / Path(f"{lengthKey}_empty.txt")
        self.outFile = oDir / Path(f"{lengthKey}_pangrams.txt")

        if not self.wordFile.is_file():
            writeWordFile(self.wordFile, minPow, maxConsonants, lengthCounts, cList, v1, v2)

        self.wordMap = readFromCache(self.wordFile, pickFirstWord)
        self.letterMap = toLetterMap(self.wordMap)

        if not self.possibleFile.is_file():
            writePossibleFile(self.possibleFile, self.letterMap, maxConsonants, v1, v2)

        # Register ctrl-C
        signal.signal(signal.SIGINT, self.exit)

    def finish(self):
        outCount = len(self.output)
        emptyCount = len(self.emptyLines)
        print(f'Saving {outCount} perfect pangram sets to {self.outFile}')
        print(f'Saving {emptyCount} unused patterns to {self.emptyFile}')
        writeLines(self.emptyFile, self.emptyLines)
        writeLines(self.outFile, self.output)

    def exit(self, s, f):
        self.finish()
        sys.exit(0)

    def readLeafList(self):
        knownEmpty = readLines(self.emptyFile)
        inList = readFromCache(self.possibleFile, flattenList)
        return [i for i in inList if i not in knownEmpty] + ['']
