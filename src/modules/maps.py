from statistics import mean
from bisect import bisect_left


def getVowelKey(s, vList):
    uniq = set(s)
    vow = [v for v in uniq if v in vList]
    cNum = len(uniq) - len(vow)
    vowX = vow if len(vow) else "x"
    return "".join([str(cNum)] + sorted(vowX))


def toLetterMap(scoreMap, vList):
    letterMap = {}
    kScoreMap = {}
    # Insure highest score combos first
    for combo, score in scoreMap.items():
        key = getVowelKey(combo, vList)
        combos = letterMap.get(key, [])
        scores = kScoreMap.get(key, [])
        newIndex = bisect_left(scores, -score)
        scores.insert(newIndex, -score)
        combos.insert(newIndex, combo)
        letterMap[key] = combos
        kScoreMap[key] = scores
    letterMap[""] = []
    return letterMap


class Maps():

    def __init__(self, wsMap, vList):
        self.wsMap = wsMap
        self.wordMap = {}
        self.scoreMap = {}
        # Insure highest score words first
        for k, ws in wsMap.items():
            words = [w for (w, s) in ws]
            wsk = ({w: -s for (w, s) in ws}).get
            self.wordMap[k] = sorted(words, key=wsk)
            scores = [s for (w, s) in ws] or [0]
            self.scoreMap[k] = mean(scores)

        self.letterMap = toLetterMap(self.scoreMap, vList)


def mapFunction(config):
    def toMaps(wsMap):
        vList = config.vList
        return Maps(wsMap, vList)
    return toMaps
