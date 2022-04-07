from .patterns import patternFunction

from sympy.solvers.diophantine.diophantine import partition
from itertools import permutations, combinations
import logging


def getDict(d, keys):
    outRoot = d
    out = outRoot
    for k in keys:
        out[k] = out.get(k, {})
        out = out[k]
    return outRoot


def setDict(d, keys):
    if not len(keys):
        return d
    return getDict(d, keys)


def sortDict(d, keys, leaf):
    if not len(d):
        return ' '.join(leaf)
    return [sortDict(d[k], keys, [*leaf, k]) for k in keys if k in d]


def toKeyTuple(line):
    vcList = zip(line["v"], line["c"])
    joined = [''.join(map(str, vc[::-1])) for vc in vcList]
    return tuple(sorted(joined, reverse=True))


def noDecrease(pairList, keys):
    for key in keys:
        matchList = [b for a, b in pairList if a == key]
        for a, b in zip(matchList, matchList[1:]):
            if a > b:
                return False
    return True


def countRepeats(tup):
    return [(t, tup[:i].count(t)) for i, t in enumerate(tup)]


def findVowelLists(vow, cons):
    vowKeys = sorted(set(vow))
    vowOrder = countRepeats(vow)
    vowCopies = [v for v in set(vow) if vow.count(v) > 1]
    for perm in permutations(vowOrder):
        # If no-vowel word occurs twice, use only one permutation
        if not noDecrease(perm, vowCopies):
            continue
        vowOut = tuple([v for v, r in perm])
        vowIndices = [vowKeys.index(v) for v in vowOut]
        # For consonant counts repeated, use only one permuation
        if not noDecrease(list(zip(cons, vowIndices)), cons):
            continue
        yield vowOut


def splitPartsWithLimit(maxPart, numTotal, num):
    for part in partition(numTotal, num):
        if part[-1] > maxPart:
            continue
        yield part


def toConsonantCounts(config):
    maxConsonants = config.maxConsonants
    cCount = len(config.cList)
    for nWords in config.wordRange():
        splitArgs = (maxConsonants, cCount, nWords)
        for part in splitPartsWithLimit(*splitArgs):
            yield part


def joinSorted(x):
    return (''.join(sorted(x)),)


def groupByPartition(pool, part):
    if not len(part):
        yield ()
        return
    for chosen in combinations(pool, part[0]):
        nextPart = part[1:]
        nextPool = pool - set(chosen)
        for rest in groupByPartition(nextPool, nextPart):
            yield joinSorted(chosen) + rest


def toVowelLists(config):
    maxVowels = config.maxVowels
    vList = config.vList
    vCount = len(vList)
    uniq = set()
    for nWords in config.wordRange():
        maxNoVowel = int(nWords - vCount / maxVowels)
        for noVowelCount in range(maxNoVowel + 1):
            nVow = nWords - noVowelCount
            splitArgs = (maxVowels, vCount, nVow)
            for part in splitPartsWithLimit(*splitArgs):
                for vCombo in groupByPartition(set(vList), part):
                    noVowelTuple = ('x',) * noVowelCount
                    out = tuple(sorted(noVowelTuple + vCombo))
                    if out not in uniq:
                        uniq.add(out)
                        yield out


def toPatterns(config):
    vcMap = {}
    for nWords in config.wordRange():
        vcMap[nWords] = {'vow': [], 'cons': []}
    for v in toVowelLists(config):
        vcMap[len(v)]["vow"].append(v)
    for c in toConsonantCounts(config):
        vcMap[len(c)]["cons"].append(c)

    total = len(vcMap.items())
    for i, kd in enumerate(vcMap.items()):
        k, d = kd
        for vow in d["vow"]:
            for cons in d["cons"]:
                for v in findVowelLists(vow, cons):
                    yield {"len": k, "v": v, "c": cons}
        logging.info(f"{k}-word patterns ({i + 1}/{total})")


def invalidate(maps, config, vcl):
    letterMap = maps.letterMap
    maxReps = config.maxReps
    repMap = {}
    for k in vcl:
        if k not in letterMap:
            return True
        if k in maxReps:
            repMap[k] = repMap.get(k, 0) + 1
            if repMap[k] > maxReps[k]:
                return True
    return False


def listPatterns(maps, config):
    patterns = list(toPatterns(config))
    vcLists = [toKeyTuple(line) for line in patterns]
    vcKeys = set([vc for vcs in vcLists for vc in vcs])
    vcKeysDescending = sorted(vcKeys, reverse=True)
    wordTree = {}
    already = set()
    for vcl in vcLists:
        invalid = invalidate(maps, config, vcl)
        if vcl in already or invalid:
            continue
        wordTree = setDict(wordTree, vcl)
        already.add(vcl)
    tree = sortDict(wordTree, vcKeysDescending, [])
    toPattern = patternFunction(config.empty)
    return toPattern(tree)
