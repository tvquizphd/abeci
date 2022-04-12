import logging

# https://link.springer.com/content/pdf/10.3758/BF03195586.pdf
PRIORS = {
    "e": 0.1255,
    "t": 0.0893,
    "a": 0.0853,
    "o": 0.0767,
    "n": 0.0735,
    "i": 0.0734,
    "s": 0.0679,
    "r": 0.0671,
    "h": 0.0479,
    "l": 0.0414,
    "d": 0.0384,
    "c": 0.0318,
    "u": 0.0262,
    "m": 0.0238,
    "f": 0.021,
    "p": 0.0204,
    "g": 0.0196,
    "y": 0.0172,
    "w": 0.0165,
    "b": 0.014,
    "v": 0.0106,
    "k": 0.0075,
    "x": 0.002,
    "z": 0.0011,
    "j": 0.0011,
    "q": 0.0009
}
MAXIMA = [0, 200, 800, 1600]


class Defaults():

    priors = PRIORS
    oDir = "results"
    eDir = "effects"
    maxRatio = 0.01
    maxCounts = {
        1: MAXIMA[1-1],
        2: MAXIMA[2-1],
        3: MAXIMA[3-1],
        "*": MAXIMA[-1]
    }
    maxReps = {
        "1x": 0,
        "2x": 1,
        "3x": 1,
        "4x": 0,
        "5x": 0,
        "6x": 0,
    }
    minWords = 4
    maxWords = 7
    maxConsonants = 6
    maxVowels = 2


def normalizePriors(priors):
    n = len(priors)
    precision = 100
    priorSum = sum(priors.values()) or 1
    if n > 0 and int(priorSum * precision) != precision:
        s = f"as sum of {priorSum} != 1.0"
        logging.warning(f"Normalizing {n} prior items {s}")
    return {k: v/priorSum for k, v in priors.items()}


def normalizeArguments(*args):
    (maxRatio, maxCounts, maxReps, priors) = args[:4]
    (minWords, maxWords, maxC, maxV) = args[4:]
    # Maximum ratio of n-letter words found
    maxRatio = maxRatio if maxRatio else Defaults.maxRatio
    # Max number of n-letter words
    maxCounts = {**Defaults.maxCounts, **maxCounts}
    # Limit words without vowels
    maxReps = {**Defaults.maxReps, **maxReps}
    # Normalized letter frequency probability distributions
    priors = normalizePriors({**Defaults.priors, **priors})

    return [
        maxRatio,
        maxCounts,
        maxReps,
        priors,
        minWords if minWords else Defaults.minWords,
        maxWords if maxWords else Defaults.maxWords,
        maxC if maxC else Defaults.maxConsonants,
        maxV if maxV else Defaults.maxVowels
    ]
