from .recounter import Recounter


def makeNewCache():
    return set([(0,)])


def compareLeaves(a, b):
    aList = a.split(' ')
    bList = b.split(' ')
    for i, (a, b) in enumerate(zip(aList, bList)):
        if a != b:
            return i + 1
    return 1


def toPangrams(files):

    cacheC = 1
    cachedLeaf = ''
    cache = makeNewCache()
    wordMap = files.wordMap
    letterMap = files.letterMap
    leafList = files.readLeafList()
    print(f'Using {len(leafList)} patterns')

    for leafIndex, (leaf, nextLeaf) in enumerate(zip(leafList, leafList[1:])):
        try:
            recounter = Recounter(leaf, letterMap, wordMap, files)
        except ValueError as e:
            print(f'impossible {e} in leaf: {leaf}')
            continue

        cacheC = compareLeaves(cachedLeaf, leaf)
        nextC = compareLeaves(leaf, nextLeaf)

        if cacheC > nextC and len(cache) == 0:
            cache = makeNewCache()

        if len(cache) > 0:
            cachedLeaf = leaf
            cache = recounter.guessNext(cache, cacheC, nextC, leafIndex)
        else:
            recounter.addEmpty(leaf)

    return files
