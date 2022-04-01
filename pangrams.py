from itertools import permutations, combinations, product
from sympy.solvers.diophantine.diophantine import partition
from google_ngram_downloader import readline_google_store
from bisect import insort
from pathlib import Path
import unidecode
import signal
import sys
import pickle 
import yaml
import math

def toVowelLists(v1, v2):
  A = list(permutations(v1, 3))
  U = list(permutations(v2, 2))
  K = [(), ("x",), ("x","x")]
  e = ("e",)

  a_ = A[0]
  u_ = U[0]

  join = lambda x,y: (''.join(sorted(x+y)),)

  for k in K:
    yield k + e + a_ + u_ #6-words
    yield k + e + a_ + join(u_[0], u_[1]) #5-words
    for u in U:
      for i, a0 in enumerate(a_):
        a1 = a_[(i + 1) % 3]
        a2 = a_[(i + 2) % 3]
        u0a0 = join(u[0],a0)
        u1a1 = join(u[1],a1)
        yield k + e + u0a0 + (u[1], a1, a2) #5-words
        yield k + e + u0a0 + u1a1 + (a2,) #4-words

def toConsonantCounts(maxConsonants):
  numTotal = 20
  minWords = 4
  maxWords = 8
  for size in range(minWords, maxWords + 1):
    for part in partition(numTotal, size): 
      if part[-1] > maxConsonants:
        continue
      yield part

def countRepeats(tup):
  return [(t, tup[:i].count(t)) for i,t in enumerate(tup)]

def noDecrease(perm, keys):
  for key in keys:
    l = [r for v, r in perm if v == key]
    for a,b in zip(l, l[1:]):
      if a > b:
        return False
  return True

def findVowelLists(vow, cons):
  vowKeys = sorted(set(vow))
  vowOrder = countRepeats(vow)
  vowCopies = [v for v in set(vow) if vow.count(v) > 1]
  for perm in permutations(vowOrder):
    # If no-vowel word occurs twice, use only one permutation
    if not noDecrease(perm, vowCopies):
      continue
    vowOut = tuple([v for v,r in perm])
    vowIndices = [vowKeys.index(v) for v in vowOut]
    # For consonant counts repeated, use only one permuation
    if not noDecrease(list(zip(cons, vowIndices)), cons):
      continue
    yield vowOut 

def showPossible(maxConsonants, v1, v2):
  minWords = 4
  maxWords = 8
  numTotal = 20
  wordRange = range(minWords, maxWords + 1)
  wordMap = {c: {'vowel': [], 'other': []} for c in wordRange}
  for v in toVowelLists(v1, v2):
    wordMap[len(v)]["vowel"].append(v)
  for c in toConsonantCounts(maxConsonants):
    wordMap[len(c)]["other"].append(c)

  total = len(wordMap.items())
  for i, kd in enumerate(wordMap.items()):
    k, d = kd
    for vow in d["vowel"]:
      for cons in d["other"]:
        for v in findVowelLists(vow, cons):
          yield {"len": k, "v": v, "c": cons}
    print(f"{i + 1} of {total}")

def toKeyTuple(line):
  vcList = zip(line["v"], line["c"])
  joined = [''.join(map(str, vc[::-1])) for vc in vcList]
  return tuple(sorted(joined, reverse=True))

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

  return True

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

def writePossibleFile(possibleFile, letterMap, maxConsonants, v1, v2):
  possible = list(showPossible(maxConsonants, v1, v2))
  wordTreeList = listWordTrees(possible, letterMap)
  print(f'writing {possibleFile}...')
  with open(possibleFile, "w") as wf:
    yaml.dump(wordTreeList, wf)

def serialCombo(c):
  return ''.join(c["combo"])

def ivParser(c):
  return {
    "combo": serialCombo(c),
    "integer": c["integer"]
  }

def setIntersect(a,b):
  return not set(a).isdisjoint(b)

def findCopies(keyList):
  keyEqualities = [a == b for a,b in zip(keyList[1:], keyList)]
  return [ i + 1 for i, x in enumerate(keyEqualities) if x]

def prettyPrint(wnl):
  w,n,l = wnl
  return w + ':' + '/'.join(map(str, [n, len(l)]))

class OutputState:

  def __init__(self, output, ivLength, cacheItem):
    self.output = output
    numC = len(cacheItem)
    cacheReader = lambda i: cacheItem[i] if i < numC else 0
    self.combIndexList = list(map(cacheReader, range(ivLength)))

class Recounter:

  def __init__(self, leaf, letterMap, wordMap, cList):

    self.leaf = leaf
    self.cList = cList
    self.wordMap = wordMap
    self.keyList = [""] + leaf.split(" ")
    self.letterList = [letterMap[k] for k in self.keyList]

  def recount(self, output, length, cacheItem):
    self.o = OutputState(output, length, cacheItem)
    loop = zip(cacheItem, self.letterList, self.keyList)
    addedStart = self.combiner(list(loop)[1:], 0)
    ivBase = [{ 'combo': '', 'integer': 0 }]
    self.ivListRoot = ivBase + addedStart 
    self.copiedKeys = findCopies(self.keyList)
    self.pivot = len(cacheItem)
    self.length = length

  def skipper(self, valid):
    return max(0, self.length - valid - 1)

  def stringifyWordList(self, words):
    letterList = self.letterList
    combIndexList = self.o.combIndexList
    iter = zip(words, combIndexList, letterList)
    return ' '.join(list(map(prettyPrint, iter))[1:])

  def logNexts(self, words):
    stats = self.stringifyWordList(words)
    return f'Result #{1+len(self.o.output)}: {stats}'

  def iterateIteration(self, skipping):
    output = [0]*skipping
    letterList = self.letterList
    combIndexList = self.o.combIndexList
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
        iv0 = self.o.combIndexList[dup - 1]
        iv1 = self.o.combIndexList[dup]
        if iv0 <= iv1:
          self.o.combIndexList = self.iterateIteration(skip)
          return (self.o.output, logList, cache)
        
    # Cache partial matches
    if len(ivList) >= nextC:
      caching = tuple(self.o.combIndexList[:nextC])
      if (cache or [()])[-1] != caching:
        cache.append(tuple(caching))

    # Update
    if isValid:
      words = finalizeCombos(self.wordMap, ivList)
      self.o.output.add(words)
      logList.append(self.logNexts(words))

    # Iterate
    self.o.combIndexList = self.iterateIteration(skipping)
    return (self.o.output, logList, cache)

  def guessNext(self, output, cache, cacheC, nextC, leafIndex):
    logMax = 4
    leaf = self.leaf
    [cached, cache] = [cache, []]
    length = len(leaf.split(' ')) + 1

    for i, cacheItem in enumerate(cached):
     
      self.recount(output, length, cacheItem)

      tries = 0
      logList = []
      outLen = len(output)
      while self.notComplete(cacheItem):
        output, logList, cache = self.handleNext(logList, cache, nextC)
        tries +=1

      # Logging
      if len(logList):
        ll = [str(len(l)) for l in self.letterList]
        prod = "x".join(ll[cacheC:])
        print(f'<leaf "count={prod}">')
        leafLog = f"Leaf #{leafIndex + 1}: {leaf}"
        matchLog = f"{len(logList)}/{tries} match"
        cacheLog = f"From {cacheC}w cache to {nextC}w cache"
        print('. '.join([leafLog, matchLog, cacheLog]))
        print('\n'.join(logList[:logMax]))
        if len(logList) > logMax:
          print('...')
        print(f"</leaf>")

    return output, cache

  def notComplete(self, cacheItem):
    lastCache = cacheItem[-1]
    cacheLength = len(cacheItem) - 1
    if self.o.combIndexList[0] != 0:
      return False
    if self.o.combIndexList[cacheLength] != lastCache:
      return False
    return True

  def verify(self, ivList):
    valid = len(ivList)
    isValid = valid == self.length 
    return isValid, self.skipper(valid)

  def maskCombo(self, c):
    bits = ""
    for a in self.cList:
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
    combIndexList = self.o.combIndexList
    allConsonants = int(self.ivListRoot[-1]["integer"])
    loop = list(zip(combIndexList, letterList, keyList))[self.pivot:]
    return self.combiner(loop, allConsonants)

def finalizeCombos(wordMap, ivList):
  getter = lambda iv: wordMap.get(iv['combo'], '')
  return tuple([getter(iv) for iv in ivList])

def compareLeaves(a,b):
  aList = a.split(' ')
  bList = b.split(' ')
  for i, (a, b) in enumerate(zip(aList, bList)):
    if a != b:
      return i + 1
  return 1

def readLines(readableFile):
  if not readableFile.is_file():
    return []
  with open(readableFile, 'r') as rf:
    return rf.read().splitlines()

def writeLines(readableFile, lines):
  mode = 'a' if readableFile.is_file() else 'w'
  with open(readableFile, mode) as wf:
    for line in lines:
      wf.write(f"{line}\n")

def makeNewCache():
  return set([(0,)])

def mainLoop(wordMap, letterMap, leafList, cList, logger):

  cacheC = 1
  cachedLeaf = ''
  output = set()
  cache = makeNewCache() 

  for leafIndex, (leaf, nextLeaf) in enumerate(zip(leafList, leafList[1:])):
    try:
      recounter = Recounter(leaf, letterMap, wordMap, cList)
    except ValueError as e:
      print(f'impossible {e} in leaf: {leaf}')
      continue 

    cacheC = compareLeaves(cachedLeaf, leaf)
    nextC = compareLeaves(leaf, nextLeaf)

    outputLength = len(output)
    if cacheC > nextC and len(cache) == 0:
      cache = makeNewCache() 

    if len(cache) > 0:
      cachedLeaf = leaf
      output, cache = recounter.guessNext(output, cache, cacheC, nextC, leafIndex)
    else:
      logger.trackEmpty(leaf)

  return output

def readFromCache(yamlFile, transform):
  pickleFile = yamlFile.with_suffix('.p')
  pickled = pickleFile.is_file()
  if pickled:
    with open(pickleFile, 'rb') as rf:
      print(f'Reading {pickleFile}...')
      return pickle.load(rf)

  with open(yamlFile, 'r') as rf:
    print(f'Reading {yamlFile}...')
    output = transform(yaml.safe_load(rf))
    if not pickled:
      print(f'Writing {pickleFile}')
      with open(pickleFile, "wb") as wf:
        pickle.dump(output, wf)
    return output

def pickFirstWord(wordLists):
  return {k: w[0] for k, w in wordLists.items()}

def toHash(list):
  return ''.join(sorted(list))

def hashWord(word):
  letterList = [c for c in set(word) if c.isalpha()]
  return toHash(letterList)

def isGoodWord(word, letters, v1, v2, maxConsonants):
  if len(word) > len(letters):
    return False 
  eCount = 1 if "e" in letters else 0
  v1Count = sum(v in letters for v in v1) 
  v2Count = sum(v in letters for v in v2) 
  vCount = sum([eCount, v1Count, v2Count])
  cCount = len(letters) - vCount
  if eCount > 0 and vCount > 1:
    return False 
  if v1Count > 1 or vCount > 2:
    return False 
  if cCount > maxConsonants:
    return False 
  return True

def flattenList(tree):
  if len(tree) == 0:
      return tree
  if isinstance(tree[0], list):
      return flattenList(tree[0]) + flattenList(tree[1:])
  return tree[:1] + flattenList(tree[1:])

def toLetterMap(wordMap):
  letterMap = {'': []}
  for combo in wordMap.keys():
    key = getVowelKey(combo) 
    combos = letterMap.get(key, [])
    letterMap[key] = [*combos, combo]
  return letterMap

def makePossibleTransformer(letterMap):

  def hasLetters(s):
    return all(i in letterMap for i in s.split(" "))

  def flattener(tree):
    list = flattenList(tree)
    return [l for l in list if hasLetters(l)]

  return flattener

def toVowels(v1, v2):
  v1v2 = (("",), ("e",),) + tuple(tuple(v) for v in v1 + v2)
  return (*v1v2, *product(v1, v2), *product(v2, v2[1:]))

def getVowelKey(s):
  uniq = set(s)
  aeiouy = "aeiouy"
  vow = [v for v in uniq if v in aeiouy]
  cNum = len(uniq) - len(vow)
  vowX = vow if len(vow) else "x" 
  return "".join([str(cNum)] + sorted(vowX))

def isWordOkay(word):
  for part in word.split("_"):
    isText = all([c.isalpha() for c in part])
    isReal = any([not c.isupper() for c in part])
    if not isText or not isReal:
      return False
  return True

def readWordRecords():
  lists = readline_google_store(ngram_len=1)
  for fname, url, records in lists:
    filename = fname.split('.')[0]
    suffix = filename.split('-')[-1]
    if len(suffix) > 1 or not suffix[0].isalpha():
      print(f'Skipping {filename}')
      continue
    for record in records:
      if record.year == 2008:
        word = unidecode.unidecode(record.ngram)
        if isWordOkay(word):
          freq = record.match_count
          yield (word.lower(), freq)

def logging(firstLetter, word, notable):
  newPage = firstLetter != word[0]
  display = f"{word[0]}:" if newPage else word
  end = "\n" if newPage else ""
  if newPage or notable: 
    print("", end=end, flush=True)
    print(display, end="", flush=True)
  return word[0]
  
def noteCopy(noted, wf):
  word = wf["w"]
  freq = wf["f"]
  try:
    copyIndex = next(i for i,v in enumerate(noted) if v["w"] == word)
    noted[copyIndex]["f"] = max(noted[copyIndex]["f"], freq)
    return True
  except StopIteration:
    return False

def countLetterSets(minPow, maxConsonants, cList, v1, v2):
  # Ignore any word with <8192 (2**13) frequency
  minimum = int(2**minPow)
  wordsByLength = {} 
  firstLetter = " "
  maxWords = 8
  # Track given number of words by length
  lengthCounts = [0, 4, 120] + [800] * (maxWords - 2)

  for (word, freq) in readWordRecords():
    letters = hashWord(word)
    length = len(letters)
    if length >= len(lengthCounts) or freq < minimum:
      continue
    if not isGoodWord(word, letters, v1, v2, maxConsonants):
      continue
    wf = {"w": word, "f": freq, "l": letters}
    sameLength = wordsByLength.get(length, [])
    # Deduplicate with maximum frequency
    if noteCopy(sameLength, wf):
      continue
    insort(sameLength, wf, key=lambda v: v["f"])
    excessCount = len(sameLength) > lengthCounts[length]
    firstLetter = logging(firstLetter, word+" ", False)
    # Remove excess words
    if excessCount:
      lostWord = sameLength.pop(0)["w"]
      logging(firstLetter, lostWord+" ", word == lostWord)

  wordsByLetter = {}
  # Higher frequencies prepended
  for sameLength in wordsByLength:
    for wf in sameLength:
      letterList = wordsByLetter.get(wf["l"], [])
      wordsByLetter[wf["l"]] = [wf["w"], *letterList]

  return wordsByLetter

def writeWordFile(wordFile, minPow, maxConsonants, cList, v1, v2):

  wordsByLetter = countLetterSets(minPow, maxConsonants, cList, v1, v2)

  print()
  print(f'writing {wordFile}...')
  with open(wordFile, "w") as wf:
    yaml.dump(wordsByLetter, wf)

  print('written.')

class Logger:

  def __init__(self, emptyFile):
    self.emptyLines = []
    self.emptyFile = emptyFile
    signal.signal(signal.SIGINT, self.exit)

  def trackEmpty(self, line):
    self.emptyLines.append(line)

  def exit(self, s, f):
    emptyCount = len(self.emptyLines)
    print(f'Adding {emptyCount} empty lines')
    writeLines(self.emptyFile, self.emptyLines)
    sys.exit(0)

def readLeafList(possibleFile, emptyFile):
  knownEmpty = readLines(emptyFile)
  inList = readFromCache(possibleFile, flattenList)
  return [i for i in inList if i not in knownEmpty] + ['']

if __name__ == "__main__":
  eDir = Path("effects")
  oDir = Path("results")
  oFile = oDir / Path("pangrams.txt")
  eDir.mkdir(parents=True, exist_ok=True)
  oDir.mkdir(parents=True, exist_ok=True)
  possibleFile = eDir / Path("possible.yaml")
  wordFile = eDir / Path("wordMap.yaml")
  emptyFile = eDir / Path("empty.txt")
  cList = 'bcdfghjklmnpqrstvwxz'
  maxConsonants = 6
  minPow = 8
  v1 = "aio"
  v2 = "yu"  

  if not wordFile.is_file():
    writeWordFile(wordFile, minPow, maxConsonants, cList, v1, v2)

  wordMap = readFromCache(wordFile, pickFirstWord)
  letterMap = toLetterMap(wordMap)

  if not possibleFile.is_file():
    writePossibleFile(possibleFile, letterMap, maxConsonants, v1, v2)

  logger = Logger(emptyFile)
  print(f"Reading {emptyFile}")
  leafList = readLeafList(possibleFile, emptyFile)
  print(f'Using {len(leafList)} patterns')
  output = mainLoop(wordMap, letterMap, leafList, cList, logger)
  print(f'Writing {oFile}')

  with open(oFile, 'w') as wf:
    for o in sorted(out):
      oStr = " ".join(o)
      wf.write(f'{oStr}\n')
