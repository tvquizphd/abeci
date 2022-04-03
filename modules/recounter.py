
def serialCombo(c):
    return ''.join(c["combo"])


def ivParser(c):
    return {
        "combo": serialCombo(c),
        "integer": c["integer"]
    }


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


def finalizeCombos(wordMap, ivList):
    return tuple([wordMap.get(iv['combo'], '') for iv in ivList])


class Recounter:

    def __init__(self, leaf, letterMap, wordMap, files):

        self.leaf = leaf
        self.files = files
        self.wordMap = wordMap
        self.keyList = [""] + leaf.split(" ")
        self.length = len(self.keyList)
        self.letterList = [letterMap[k] for k in self.keyList]

    def addOutput(self, words):
        self.files.output.append(" ".join(words))

    def addEmpty(self, line):
        self.files.emptyLines.append(line)

    def recount(self, cacheItem):
        self.combIndexList = makeIndexList(self.length, cacheItem)
        loop = zip(cacheItem, self.letterList, self.keyList)
        addedStart = self.combiner(list(loop)[1:], 0)
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
        outCount = 1 + len(self.files.output)
        stats = self.stringifyWordList(words)
        return f'Result #{outCount}: {stats}'

    def iterateIteration(self, skipping):
        output = [0]*skipping
        letterList = self.letterList
        combIndexList = self.combIndexList
        iter = list(zip(combIndexList, letterList))
        for n, l in iter[::-1][skipping:]:
            nexts = n + 1
            count = len(l)
            if nexts < count:
                output = [nexts] + output
                break
            output = [0] + output

        if len(combIndexList) == len(output):
            return [1] + output[1:]
        pivot = len(combIndexList)-len(output)
        return combIndexList[:pivot] + output

    def handleNext(self, logList, cache, nextC):

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
                    return (logList, cache)

        # Cache partial matches
        if len(ivList) >= nextC:
            caching = tuple(self.combIndexList[:nextC])
            if (cache or [()])[-1] != caching:
                cache.append(tuple(caching))

        # Update
        if isValid:
            words = finalizeCombos(self.wordMap, ivList)
            logList.append(self.logNexts(words))
            self.addOutput(words)

        # Iterate
        self.combIndexList = self.iterateIteration(skipping)
        return (logList, cache)

    def guessNext(self, cache, cacheC, nextC, leafIndex):
        logMax = 4
        leaf = self.leaf
        [cached, cache] = [cache, []]

        for i, cacheItem in enumerate(cached):

            self.recount(cacheItem)

            tries = 0
            logList = []
            while self.notComplete(cacheItem):
                logList, cache = self.handleNext(logList, cache, nextC)
                tries += 1

            # Logging
            if len(logList):
                lengths = [str(len(letters)) for letters in self.letterList]
                pIndex = leafIndex + 1
                prod = "x".join(lengths[cacheC:])
                print(f'<result var="{prod}" pattern="{pIndex}">')
                matchLog = f"{len(logList)}/{tries} match"
                cacheLog = f"From {cacheC}w cache to {nextC}w cache"
                print('. '.join([leaf, matchLog, cacheLog]))
                print('\n'.join(logList[:logMax]))
                if len(logList) > logMax:
                    print('...')
                print("</result>")

        return cache

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
        for a in self.files.cList:
            bits += "1" if a in c else "0"
        return int(bits, 2)

    def combiner(self, loop, allConsonants):
        combos = []
        for next, letters, key in loop:
            if next >= len(letters):
                break
            combo = list(letters[next])
            integer = self.maskCombo(combo)
            if (allConsonants & integer) != 0:
                break
            allConsonants |= integer
            out = {"combo": combo, "integer": allConsonants}
            combos.append(ivParser(out))
        return combos

    def combine(self):
        keyList = self.keyList
        letterList = self.letterList
        combIndexList = self.combIndexList
        allConsonants = int(self.ivListRoot[-1]["integer"])
        loop = list(zip(combIndexList, letterList, keyList))[self.pivot:]
        return self.combiner(loop, allConsonants)
