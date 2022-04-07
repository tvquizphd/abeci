import logging

from .recounter import Recounter
from .cache import Cache


def compareLeaves(a, b):
    aList = a.split(' ')
    bList = b.split(' ')
    for i, (a, b) in enumerate(zip(aList, bList)):
        if a != b:
            return i + 1
    return 1


def toPangrams(maps, patterns, config):

    cachedLeaf = ''
    leafList = patterns.list
    cache = Cache([(0,)], (1, 0))
    logging.info(f'Using {len(leafList)} patterns')

    for leafIndex, (leaf, nextLeaf) in enumerate(zip(leafList, leafList[1:])):
        try:
            recounter = Recounter(maps, config, leaf)
        except ValueError as e:
            logging.error(f'impossible {e} in leaf: {leaf}')
            continue

        cacheC = compareLeaves(cachedLeaf, leaf)
        nextC = compareLeaves(leaf, nextLeaf)
        cache.updateCounts(cacheC, nextC)

        if not cache.isEmpty:
            cachedLeaf = leaf
            cache = recounter.guessNext(cache, leafIndex)

    return config
