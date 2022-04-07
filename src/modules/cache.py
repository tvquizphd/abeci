class Cache():

    def __init__(self, items, counts):
        self.counts = counts
        self.items = items

    def __iter__(self):
        for i, item in enumerate(self.items):
            yield (i, item)

    def clearEmptyAndUncertain(self, cleared):
        isEmpty = self.isEmpty
        isCertain = self.isCertain
        if isEmpty and not isCertain:
            self.items = cleared

    def updateCounts(self, c0, c1):
        self.counts = (c0, c1)
        self.clearEmptyAndUncertain([(0,)])

    @property
    def isEmpty(self):
        return len(self.items) == 0

    @property
    def isCertain(self):
        c0, c1 = self.counts
        return c0 <= c1

    @property
    def latest(self):
        return (self.items or [()])[-1]

    def toNew(self):
        counts = self.counts
        return Cache([], counts)

    def isEnough(self, count):
        c1 = self.counts[1]
        return count >= c1

    def addItem(self, indexList):
        c1 = self.counts[1]
        caching = tuple(indexList[:c1])
        if self.latest != caching:
            self.items.append(tuple(caching))
