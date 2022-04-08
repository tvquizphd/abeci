from .logging import ResultLogger

from itertools import product


def findCopies(keyList):
    keyEqualities = [a == b for a, b in zip(keyList[1:], keyList)]
    return [i + 1 for i, x in enumerate(keyEqualities) if x]


def prettyPrint(wnl):
    w, n, letters = wnl
    return w + ':' + '/'.join(map(str, [n, len(letters)]))


def makeIndexList(ivLength, cacheItem):
    numC = len(cacheItem)

    def cacheReader(i):
        return cacheItem[i] if i < numC else 0

    return list(map(cacheReader, range(ivLength)))


def yieldWords(wordMap, ivList, showAll):
    letterList = [iv['combo'] for iv in ivList]
    wordLists = [wordMap.get(c, ['']) for c in letterList]
    if showAll:
        for words in product(*wordLists):
            yield tuple(words)
    else:
        yield tuple([words[0] for words in wordLists])


class Recounter:

    def __init__(self, maps, config, leaf):

        letterMap = maps.letterMap
        keyList = [""] + leaf.split(" ")
        self.letterList = [letterMap[k] for k in keyList]
        self.wordMap = maps.wordMap
        self.length = len(keyList)
        self.keyList = keyList
        self.config = config
        self.leaf = leaf

    def addOutput(self, words):
        self.config.addOutput(words)

    def addEmpty(self, line):
        self.config.addEmpty(line)

    def recount(self, cacheItem):
        self.combIndexList = makeIndexList(self.length, cacheItem)
        zipped = zip(cacheItem, self.letterList, self.keyList)
        addedStart = self.combiner(list(zipped)[1:], 0)
        ivBase = [{'combo': '', 'integer': 0}]
        self.ivListRoot = ivBase + addedStart
        self.copiedKeys = findCopies(self.keyList)
        self.pivot = len(cacheItem)

    def skipper(self, valid):
        return max(0, self.length - valid - 1)

    def stringifyWordList(self, words):
        letterList = self.letterList
        combIndexList = self.combIndexList
        iter = zip(words, combIndexList, letterList)
        return ' '.join(list(map(prettyPrint, iter))[1:])

    def logNexts(self, words):
        outCount = self.config.outputLength
        stats = self.stringifyWordList(words)
        return f'Result #{outCount}: {stats}'

    def iterateIteration(self, skipping):
        newIndexList = [0]*skipping
        letterList = self.letterList
        combIndexList = self.combIndexList
        iter = list(zip(combIndexList, letterList))
        for n, l in iter[::-1][skipping:]:
            nexts = n + 1
            count = len(l)
            if nexts < count:
                newIndexList = [nexts] + newIndexList
                break
            newIndexList = [0] + newIndexList

        if len(combIndexList) == len(newIndexList):
            return [1] + newIndexList[1:]
        pivot = len(combIndexList) - len(newIndexList)
        return combIndexList[:pivot] + newIndexList

    def handleNext(self, logger, newCache):

        copiedKeys = self.copiedKeys

        ivList = self.ivListRoot + self.combine()
        isValid, skipping = self.verify(ivList)

        # Ensure no duplicates among identical keys
        # Identical keys like "3x" are possible
        for dup in copiedKeys:
            skip = self.skipper(dup)
            if skip >= skipping:
                iv0 = self.combIndexList[dup - 1]
                iv1 = self.combIndexList[dup]
                if iv0 <= iv1:
                    self.combIndexList = self.iterateIteration(skip)
                    return newCache

        # Cache partial matches
        if newCache.isEnough(len(ivList)):
            newCache.addItem(self.combIndexList)

        # Update
        if isValid:
            showAll = self.config.showAll
            for words in yieldWords(self.wordMap, ivList, showAll):
                logger.add(self.logNexts(words))
                self.addOutput(words)

        # Iterate
        self.combIndexList = self.iterateIteration(skipping)
        logger.tries += 1
        return newCache

    def guessNext(self, cache, leafIndex):
        shh = self.config.shh
        newCache = cache.toNew()
        letterList = self.letterList
        logArgs = (letterList, leafIndex, newCache)
        logger = ResultLogger(shh, *logArgs)

        for i, cacheItem in cache:

            self.recount(cacheItem)

            while self.notComplete(cacheItem):
                newCache = self.handleNext(logger, newCache)

        if not shh or leafIndex % 100 == 0:
            logger.log(self.leaf, leafIndex)
            if len(logger.logList) < 0:
                self.addEmpty(self.leaf)

        return newCache

    def notComplete(self, cacheItem):
        lastCache = cacheItem[-1]
        cacheLength = len(cacheItem) - 1
        if self.combIndexList[0] != 0:
            return False
        if self.combIndexList[cacheLength] != lastCache:
            return False
        return True

    def verify(self, ivList):
        valid = len(ivList)
        isValid = valid == self.length
        return isValid, self.skipper(valid)

    def maskCombo(self, c):
        bits = ""
        for a in self.config.cList:
            bits += "1" if a in c else "0"
        return int(bits, 2)

    def combiner(self, zipped, allConsonants):
        combos = []
        for next, letters, key in zipped:
            if next >= len(letters):
                break
            combo = list(letters[next])
            integer = self.maskCombo(combo)
            if (allConsonants & integer) != 0:
                break
            allConsonants |= integer
            out = {
                "combo": ''.join(combo),
                "integer": allConsonants
            }
            combos.append(out)
        return combos

    def combine(self):
        keyList = self.keyList
        letterList = self.letterList
        combIndexList = self.combIndexList
        allConsonants = int(self.ivListRoot[-1]["integer"])
        zipped = list(zip(combIndexList, letterList, keyList))[self.pivot:]
        return self.combiner(zipped, allConsonants)
