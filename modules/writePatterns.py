from sympy.solvers.diophantine.diophantine import partition
from itertools import permutations

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


def listWordTrees(possible, letterMap):
    vcLists = [toKeyTuple(line) for line in possible]
    vcKeys = set([vc for vcs in vcLists for vc in vcs])
    vcKeysDescending = sorted(vcKeys, reverse=True)
    wordTree = {}
    already = set()
    for vcl in vcLists:
        invalid = (k not in letterMap for k in vcl)
        if vcl in already or any(invalid):
            continue
        wordTree = setDict(wordTree, vcl)
        already.add(vcl)
    wordTreeList = sortDict(wordTree, vcKeysDescending, [])
    return wordTreeList


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


def toConsonantCounts(maxConsonants, numTotal, minWords, maxWords):
    for size in range(minWords, maxWords + 1):
        for part in partition(numTotal, size):
            if part[-1] > maxConsonants:
                continue
            yield part


def joinSorted(x, y):
    return (''.join(sorted(x+y)),)


def toVowelLists(v1, v2):
    A = list(permutations(v1, 3))
    U = list(permutations(v2, 2))
    K = [(), ("x",), ("x", "x")]
    e = ("e",)

    a_ = A[0]
    u_ = U[0]

    for k in K:
        yield k + e + a_ + u_
        yield k + e + a_ + joinSorted(u_[0], u_[1])
        for u in U:
            for i, a0 in enumerate(a_):
                a1 = a_[(i + 1) % 3]
                a2 = a_[(i + 2) % 3]
                u0a0 = joinSorted(u[0], a0)
                u1a1 = joinSorted(u[1], a1)
                yield k + e + u0a0 + (u[1], a1, a2)
                yield k + e + u0a0 + u1a1 + (a2,)


def showPossible(maxConsonants, v1, v2):
    minWords = 4
    maxWords = 8
    numTotal = 20
    wordRange = range(minWords, maxWords + 1)
    wordMap = {c: {'vowel': [], 'other': []} for c in wordRange}
    for v in toVowelLists(v1, v2):
        wordMap[len(v)]["vowel"].append(v)
    for c in toConsonantCounts(maxConsonants, numTotal, minWords, maxWords):
        wordMap[len(c)]["other"].append(c)

    total = len(wordMap.items())
    for i, kd in enumerate(wordMap.items()):
        k, d = kd
        for vow in d["vowel"]:
            for cons in d["other"]:
                for v in findVowelLists(vow, cons):
                    yield {"len": k, "v": v, "c": cons}
        print(f"{i + 1} of {total}")


def writePossibleFile(possibleFile, letterMap, maxConsonants, v1, v2):
    possible = list(showPossible(maxConsonants, v1, v2))
    wordTreeList = listWordTrees(possible, letterMap)
    print(f'writing {possibleFile}...')
    with open(possibleFile, "w") as wf:
        yaml.dump(wordTreeList, wf)
