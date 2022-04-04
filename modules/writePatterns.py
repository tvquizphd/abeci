from sympy.solvers.diophantine.diophantine import partition
from itertools import permutations, combinations

import yaml


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


def toConsonantCounts(maxConsonants, numTotal, wordRange):
    for nWords in wordRange:
        for part in splitPartsWithLimit(maxConsonants, numTotal, nWords):
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


def toVowelLists(maxVowels, wordRange):
    vList = list("aeiouy")
    vCount = len(vList)
    uniq = set()
    for nWords in wordRange:
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


def toPatterns(maxConsonants, maxVowels):
    minWords = 4
    maxWords = 8
    numTotal = 20
    wordRange = list(range(minWords, maxWords + 1))
    wordMap = {c: {'vowel': [], 'other': []} for c in wordRange}
    for v in toVowelLists(maxVowels, wordRange):
        wordMap[len(v)]["vowel"].append(v)
    for c in toConsonantCounts(maxConsonants, numTotal, wordRange):
        wordMap[len(c)]["other"].append(c)

    total = len(wordMap.items())
    for i, kd in enumerate(wordMap.items()):
        k, d = kd
        for vow in d["vowel"]:
            for cons in d["other"]:
                for v in findVowelLists(vow, cons):
                    yield {"len": k, "v": v, "c": cons}
        print(f"{i + 1} of {total}")


def invalidate(letterMap, maxReps, vcl):
    repMap = {}
    for k in vcl:
        if k not in letterMap:
            return True
        if k in maxReps:
            repMap[k] = repMap.get(k, 0) + 1
            if repMap[k] > maxReps[k]:
                return True
    return False


def listWordTrees(possible, letterMap, maxReps):
    vcLists = [toKeyTuple(line) for line in possible]
    vcKeys = set([vc for vcs in vcLists for vc in vcs])
    vcKeysDescending = sorted(vcKeys, reverse=True)
    wordTree = {}
    already = set()
    for vcl in vcLists:
        invalid = invalidate(letterMap, maxReps, vcl)
        if vcl in already or invalid:
            continue
        wordTree = setDict(wordTree, vcl)
        already.add(vcl)
    wordTreeList = sortDict(wordTree, vcKeysDescending, [])
    return wordTreeList


def writePatterns(possibleFile, letterMap, maxReps, maxConsonants, maxVowels):
    possible = list(toPatterns(maxConsonants, maxVowels))
    wordTreeList = listWordTrees(possible, letterMap, maxReps)
    print(f'writing {possibleFile}...')
    with open(possibleFile, "w") as wf:
        yaml.dump(wordTreeList, wf)
