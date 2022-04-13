import unittest

from abeci.maps import Maps


class InData():

    def __init__(self, wsMap, vList):
        self.wsMap = wsMap
        self.vList = vList


class OutData():

    def __init__(self, inData, wordMap, scoreMap, letterMap):
        self.wsMap = inData.wsMap
        self.wordMap = wordMap
        self.scoreMap = scoreMap
        self.letterMap = letterMap


class Data():

    def __init__(self, test, wsMap, vList, *args):
        self.test = test
        self.args = InData(wsMap, vList)
        self.out = OutData(self.args, *args)

    def testDictOfList(self, m0, m1):
        test = self.test
        test.assertEqual(len(m0), len(m1))
        for k in m0.keys():
            v0, v1 = [m[k] for m in (m0, m1)]
            test.assertEqual(len(v0), len(v1))
            for w0, w1 in zip(v0, v1):
                test.assertEqual(len(w0), len(w1))

    def testMaps(self, maps):
        self.testWordMap(maps)
        self.testScoreMap(maps)
        self.testLetterMap(maps)

    def testWordMap(self, maps):
        m0 = self.out.wordMap
        m1 = maps.wordMap
        self.testDictOfList(m0, m1)

    def testLetterMap(self, maps):
        m0 = self.out.letterMap
        m1 = maps.letterMap
        self.testDictOfList(m0, m1)

    def testScoreMap(self, maps):
        test = self.test
        m0 = self.out.scoreMap
        m1 = maps.scoreMap
        test.assertEqual(len(m0), len(m1))
        for k in m0.keys():
            v0, v1 = [m[k] for m in (m0, m1)]
            test.assertEqual(v0, v1)


A = [
    (
        {
            "act": [["cat", 10], ["act", 3.14], ["tac", 0.1]]
        },
        "aeiouy",
        {
            "act": ["cat", "act", "tac"]
        },
        {
            "act": 4.413333333333333333
        },
        {
            "2a": ["act"],
            "": []
        }
    ),
    (
        {
            "act": [["cat", 10], ["act", 3.14], ["tac", 0.1]],
            "imp": [["pim", 99], ["imp", 0.9], ["mip", 0.1]],
            "dik": [["kid", 99], ["idk", 1]]
        },
        "aeiouy",
        {
            "act": ["cat", "act", "tac"],
            "imp": ["pim", "imp", "mip"],
            "dik": ["kid", "idk"]
        },
        {
            "act": 4.413333333333333333,
            "imp": 33.33333333333333333,
            "dik": 50
        },
        {
            "2a": ["act"],
            "2i": ["dik", "imp"],
            "": []
        }
    )
]


class TestMapsClass(unittest.TestCase):

    def test_maps_exist(self):
        D = [Data(self, *args) for args in A]
        for datum in D:
            wsMap = datum.args.wsMap
            vList = datum.args.vList
            maps = Maps(wsMap, vList)
            datum.testMaps(maps)


if __name__ == '__main__':
    unittest.main()
