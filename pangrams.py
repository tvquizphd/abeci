from itertools import permutations, combinations, product
from sympy.solvers.diophantine.diophantine import partition
from google_ngram_downloader import readline_google_store
from pathlib import Path
import unidecode
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

def listWordTrees(possible):
  vcLists = [toKeyTuple(line) for line in possible]
  vcKeys = set([vc for vcs in vcLists for vc in vcs])
  vcKeysDescending = sorted(vcKeys, reverse=True)
  wordTree = {}
  already = set()
  for vcl in vcLists:
    if (vcl not in already):
      wordTree = setDict(wordTree, vcl)
      already.add(vcl)
  wordTreeList = sortDict(wordTree, vcKeysDescending, [])
  return wordTreeList

def writePossibleFile(possibleFile, maxConsonants, v1, v2):
  possible = list(showPossible(maxConsonants, v1, v2))
  wordTreeList = listWordTrees(possible)
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

  def __init__(self, output, ivList, cacheItem):
    self.output = output
    numC = len(cacheItem)
    cacheReader = lambda i: cacheItem[i] if i < numC else 0
    self.combIndexList = list(map(cacheReader, range(len(ivList))))

class Recounter:

  def __init__(self, leaf, letterMap, wordMap, cList):

    self.leaf = leaf
    self.cList = cList
    self.wordMap = wordMap
    self.letterMap = letterMap
    self.keyList = [""] + leaf.split(" ")
    self.letterList = []
    for k in self.keyList:
      if k not in letterMap:
        raise ValueError(k)
      self.letterList.append(letterMap[k])

  def recount(self, output, ivList, cacheItem):
    self.length = len(ivList)
    self.copiedKeys = findCopies(self.keyList)
    self.o = OutputState(output, ivList, cacheItem)
    ivListRoot = [iv for iv in ivList if len(iv.keys()) > 1]
    self.pivot = len(ivListRoot)
    self.ivListRoot = ivListRoot

  def skipper(self, valid):
    return max(0, self.length - valid - 1)

  def stringifyWordList(self, words):
    letterList = self.letterList
    combIndexList = self.o.combIndexList
    iter = zip(words, combIndexList, letterList)
    return ' '.join(list(map(prettyPrint, iter))[1:])

  def printNexts(self, words):
    stats = self.stringifyWordList(words)
    print(f'Item #{1+len(self.o.output)} {self.leaf}: {stats}')

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

  def handleNext(self, cache, nextC, ivList):

    copiedKeys = self.copiedKeys
    ivListRoot = self.ivListRoot

    added = self.combine()
    ivListNew = ivListRoot + added
    isValid, skipping = self.verify(ivListNew)

    for valid in copiedKeys:
      skip = self.skipper(valid)
      if skip >= skipping:
        iv0 = self.o.combIndexList[valid - 1]
        iv1 = self.o.combIndexList[valid]
        if iv0 <= iv1:
          self.o.combIndexList = self.iterateIteration(skip)
          return (self.o.output, ivList, cache)
        
    if len(ivListNew) >= nextC:
      caching = self.o.combIndexList[:nextC]
      cache.add(tuple(caching))

    words = finalizeCombos(self.wordMap, ivListNew)

    if isValid:
      words = finalizeCombos(self.wordMap, ivListNew)
      if words not in self.o.output:
        self.o.output.append(words)
        ivList = ivListNew
      else:
        print(end='!', flush=True)
        self.o.combIndexList = self.iterateIteration(self.length - 1)
      # Logging
      if len(self.o.output) % 10000 == 0:
        print()
        self.printNexts(words)
      elif len(self.o.output) % 1000 == 0:
        print(end='o', flush=True)

    self.o.combIndexList = self.iterateIteration(skipping)
    return (self.o.output, ivList, cache)

  def guessNext(self, output, ivList, cache, cacheC, nextC):
    leaf = self.leaf
    emptyLength = len(leaf.split(' ')[cacheC:])
    ivEmptyNew = [{} for _ in range(emptyLength + 1)]
    ivList = ivList[:cacheC] + ivEmptyNew
    iter = list(cache)
    cache = set()

    print()
    cacheLog = (f'Cached {cacheC}w', f'Caching {nextC}w')
    print('. '.join([leaf, f'{len(output)} pangrams found', *cacheLog]))

    for i, cacheItem in enumerate(iter):
     
      self.recount(output, ivList, cacheItem)

      #Logging
      if i % max(len(iter) // 20, 1) == 0:
        print(f'Cache {i}/{len(iter)}', end=' ', flush=True)

      while self.notComplete(cacheItem):
        output, ivList, cache = self.handleNext(cache, nextC, ivList)

    return output, ivList, cache

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

  def combine(self):
    keyList = self.keyList
    letterMap = self.letterMap
    letterList = self.letterList
    combIndexList = self.o.combIndexList
    allConsonants = 0 
    combos = []
    for next, letters, key in list(zip(combIndexList, letterList, keyList))[self.pivot:]:
      if next >= len(letters):
        break
      combo = list(letters[next])
      integer = self.maskCombo(combo)
      if (allConsonants & integer) != 0:
        break
      out = {"combo": combo, "integer": integer}
      allConsonants |= integer
      combos.append(ivParser(out))
    return combos 

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

def writeLine(readableFile, line):
  mode = 'a' if readableFile.is_file() else 'w'
  with open(readableFile, mode) as wf:
    wf.write(line+"\n")

def makeNewCache():
  return set([(0,)])

def leafValue(wordMap, letterMap, input, emptyFile, cList):

  output = []
  cacheC = 1
  cachedLeaf = ''
  cache = makeNewCache() 
  knownEmpty = readLines(emptyFile)
  ivList = [{ 'combo': '', 'integer': 0 }]
  leafList = [i for i in input if i not in knownEmpty]

  print(f'Looping through {len(leafList)} leaves')
  for (leaf, nextLeaf) in zip(leafList, leafList[1:]):

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
      output, ivList, cache = recounter.guessNext(output, ivList, cache, cacheC, nextC)

    if len(output) == outputLength:
      writeLine(emptyFile, leaf)

  return output

def readFromCache(yamlFile, transform):
  pickleFile = yamlFile.with_suffix('.p')
  pickled = pickleFile.is_file()
  if pickled:
    with open(pickleFile, 'rb') as rf:
      print(f'reading {pickleFile}...')
      return pickle.load(rf)

  with open(yamlFile, 'r') as rf:
    print(f'reading {yamlFile}...')
    output = transform(yaml.safe_load(rf))
    if not pickled:
      print(f'Writing {pickleFile}')
      with open(pickleFile, "wb") as wf:
        pickle.dump(output, wf)
    return output

def transformCounts(letterCounts):
  return letterCounts 

def transformWords(wordLists):
  output = {}
  for key, words in wordLists.items():
    output[key] = words[0]
  return output

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

def readLetterMap(countFile, transformCounts):
  counts = readFromCache(countFile, transformCounts)
  nonZeroSets = [k for k,v in counts.items() if v > 0]
  letterMap = {'': []}
  for s in nonZeroSets:
    key = getVowelKey(s) 
    vm = letterMap.get(key, [])
    letterMap[key] = [*vm, s]
  return letterMap

def makePossibleTransformer(letterMap):

  def hasLetters(s):
    return all(i in letterMap for i in s.split(" "))

  def flattener(tree):
    list = flattenList(tree)
    return [l for l in list if hasLetters(l)]

  return flattener

def readFiles(possibleFile, emptyFlie, wordFiles, maxConsonants, cList, v1, v2):
  countFile = wordFiles["counts"]
  listFile = wordFiles["lists"]
  letterMap = readLetterMap(countFile, transformCounts)

  wordMap = readFromCache(listFile, transformWords)
  transformPossible = makePossibleTransformer(letterMap)
  input = readFromCache(possibleFile, transformPossible) + ['']

  print('ready') 
  output = leafValue(wordMap, letterMap, input, emptyFile, cList)
  return output

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
  
def minMap(q):
  # Estimates for fraction of non-noise hits
  # Words with more letters have less noise
  targets = {
    1: 0.1,
    2: 0.1,
    3: 0.1,
    4: 0.3,
    5: 0.5,
    6: 1.0,
    7: 1.0,
    8: 1.0,
  }
  output = {}
  isInt = lambda i: isinstance(i, int)
  for t,target in targets.items():
    stats = q.get(t, {})
    keys = sorted([i for i in stats.keys() if isInt(i)])
    for f in keys[::-1]:
      atLeast = stats[f]
      if atLeast >= target:
        output[t] = f
        break
    if t not in output: 
      output[t] = 0
  return output

def countLetterSets(minPow, maxConsonants, q, cList, v1, v2):
  # Ignore any word with <8192 (2**13) frequency
  minima = int(2**minPow)
  letterDict = {}
  notableWords = {} 
  firstLetter = " "

  mapped = minMap(q)
  minWord = min(mapped.keys())
  maxWord = max(mapped.keys())
  idxMap = lambda w: mapped[min(max(len(w),minWord),maxWord)]
  print(mapped)

  for (word, freq) in readWordRecords():
    letters = hashWord(word)
    if not isGoodWord(word, letters, v1, v2, maxConsonants):
      continue
    if freq < max(minima, idxMap(word)):
      continue
    wf = {"w": word, "f": freq}
    noted = notableWords.get(letters,[])
    if word in [w["w"] for w in noted]:
      continue
    notableWords[letters] = [*noted, wf]
    counted = letterDict.get(letters, 0)
    letterDict[letters] = counted + 1
    firstLetter = logging(firstLetter, word+" ", True)

  for k in notableWords.keys():
    notableWords[k].sort(key=lambda v: v["f"], reverse=True)
    notableWords[k] = [v["w"] for v in notableWords[k]]

  return (letterDict, notableWords)

def writeWordFiles(wordFiles, qFile, minPow, maxConsonants, cList, v1, v2):
  with open(qFile, "r") as rf:
    q = yaml.safe_load(rf)

  letterDict, notableWords = countLetterSets(minPow, maxConsonants, q, cList, v1, v2)
  countFile = wordFiles["counts"]
  listFile = wordFiles["lists"]

  print()
  print(f'writing {countFile}...')
  with open(countFile, "w") as wf:
    yaml.dump(letterDict, wf)

  print(f'writing {listFile}...')
  with open(listFile, "w") as wf:
    yaml.dump(notableWords, wf)

  print('written.')

def writeQ(qFile, minPow, maxConsonants, v1, v2):
  items = {}
  allWords = set()
  firstLetter = " "
  for (word, freq) in readWordRecords():
    letters = hashWord(word)
    if not isGoodWord(word, letters, v1, v2, maxConsonants):
      continue
    if freq < 2**minPow:
      continue
    if word in allWords:
      continue
    allWords.add(word)
    wordLen = len(word)
    items[wordLen] = items.get(wordLen, []) + [freq]
    firstLetter = logging(firstLetter, word+" ", False)

  sumItems = {k: {} for k in items.keys()}
  outItems = {k: {} for k in items.keys()}

  for k,v in items.items():
    mean = sum(v)/len(v)
    sumItems[k]["mean"] = mean
    s2 = [(i - mean)**2 for i in v]
    sumItems[k]["std"] = math.sqrt(sum(s2)/len(v))

  for k,v in items.items():
    vCount = len(v)
    std = sumItems[k]["std"]
    mean = sumItems[k]["mean"]
    outItems[k]["n"] = vCount
    maxPow = math.floor(math.log2(mean))
    smallerPower = range(minPow, maxPow)
    smaller = [int(2**p) for p in smallerPower]
    bigger = [int(mean + d*std) for d in range(5)]
    for freq in smaller + bigger:
      q = len([i for i in v if i > freq])
      outItems[k][freq] = q / vCount 

  with open(qFile, "w") as wf:
    yaml.dump(outItems, wf)

if __name__ == "__main__":
  qFile = Path("stats.yaml")
  possibleFile = Path("possible.yaml")
  emptyFile = Path("empty.txt")
  wordFiles = {
    "counts": Path("letterCounts.yaml"),
    "lists": Path("wordLists.yaml")
  }
  cList = 'bcdfghjklmnpqrstvwxz'
  maxConsonants = 6
  minPow = 10
  v1 = "aio"
  v2 = "yu"  

  if not possibleFile.is_file():
    writePossibleFile(possibleFile, maxConsonants, v1, v2)

  if not qFile.is_file():
    writeQ(qFile, minPow, maxConsonants, v1, v2)

  if not all(f.is_file() for f in wordFiles.values()):
    writeWordFiles(wordFiles, qFile, minPow, maxConsonants, cList, v1, v2)

  out = readFiles(possibleFile, emptyFile, wordFiles, maxConsonants, cList, v1, v2)
  with open('output.p', 'wb') as wf:
    pickle.dump(out, wf)
