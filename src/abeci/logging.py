import logging
import math


def logMaxCounts(maxCounts):
    mk = list(maxCounts.keys())
    text = 'must include "*" key'
    keys = ','.join(map(str, mk))
    return f"Keys {keys} of maxCounts {text}"


def roughLog(v):
    return 2 ** int(math.log2(max(1, math.log(v))))


class DeltaLogger():

    def __init__(self, shh):
        self.lastFirstLetter = " "
        self.logFirsts = (" ", " ")
        self.deltas = {"+": 0, "-": 0}
        self.logLen = None if shh else 500
        self.colon = ": ..." if shh else ":"

    def log(self, over, logWord, word):
        sym = "-" if over else "+"
        self.deltas[sym] += 1

        if self.logLen is not None:
            if self.deltas[sym] >= self.logLen:
                self.deltas[sym] = 0
                logText = f"{sym}{logWord}, "
                logging.info(logText)

        fw = word[0]
        f0, f1 = self.logFirsts
        ff = self.lastFirstLetter

        if fw != ff and f0 == ff and fw == f1:
            self.lastFirstLetter = fw
            logging.info(f"\n{fw}{self.colon}")

        self.logFirsts = (f1, fw)


class CutLogger():

    def __init__(self, shh):
        self.wordCount = 0
        self.cutWordCount = 0
        self.cutWordLogs = []
        self.shh = shh

    def add(self, wList, maxAllowed):
        cutKeyCount = max(0, len(wList) - maxAllowed)
        self.cutWordCount += cutKeyCount
        self.wordCount += len(wList)
        if self.shh:
            return
        if cutKeyCount > 0:
            bestCut = wList[cutKeyCount - 1].word
            phrase = [str(cutKeyCount), "like", bestCut]
            self.cutWordLogs.append(" ".join(phrase))

    def log(self, maxRatio):
        wc = self.wordCount
        cwc = self.cutWordCount
        ratio = 100 * maxRatio
        logging.info("")
        logging.debug(wc, cwc)
        if cwc > 0:
            cut = int(1000 * cwc / wc) / 10
            cutLog = f"cut {cut}% of {wc} words"
            logging.info(f"The {ratio}% has {cutLog}:")
            if len(self.cutWordLogs):
                logging.info(", ".join(self.cutWordLogs))
        else:
            logging.info(f"No word types exceed {ratio}% limit.")


def strLen(items):
    return str(len(items))


class ResultLogger():

    def __init__(self, shh, letterList, leafIndex, newCache):
        c0, c1 = newCache.counts
        lengths = list(map(strLen, letterList))
        variables = lengths[c0:]
        prod = "x".join(variables)
        self.debugList = [
            f'Seached <{prod} sentences"',
            f"From {c0}w cache to {c1}w cache",
        ]
        self.logList = []
        self.tries = 0
        self.shh = shh

    def add(self, item):
        self.logList.append(item)

    def log(self, leaf, leafIndex):
        debugList = self.debugList
        logList = self.logList
        tries = self.tries
        logLen = len(logList)
        if logLen:
            logging.info(f"Pattern #{1 + leafIndex}, ")
            if not self.shh:
                debugLog = " ".join(debugList + logList[:1])
                logging.info(f"Found {logLen}/{tries}, ")
                logging.debug(debugLog + ", ")
                logging.info("")
