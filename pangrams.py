from modules.fileHandler import FileHandler
from modules.toPangrams import toPangrams

import math
from pathlib import Path

# https://link.springer.com/content/pdf/10.3758/BF03195586.pdf
# TODO... is helpful?
BASELINE = {
}
'''
    'e': 3.26,
    't': 2.32,
    'a': 2.21,
    'o': 1.99,
    'n': 1.91,
    'i': 1.90,
    's': 1.76,
    'r': 1.74,
    'h': 1.24,
    'l': 1.07,
    'd': 0.99,
    'c': 0.82,
    'u': 0.68,
    'm': 0.61,
    'f': 0.54,
    'p': 0.52,
    'g': 0.50,
    'y': 0.44,
    'w': 0.42,
    'b': 0.36,
    'v': 0.27,
    'k': 0.19,
    'x': 0.05,
    'z': 0.02
}
'''


def countCombos(itemCount, comboRange):
    return sum([math.comb(itemCount, q) for q in comboRange])


if __name__ == "__main__":
    eDir = Path("effects")
    oDir = Path("results")
    eDir.mkdir(parents=True, exist_ok=True)
    oDir.mkdir(parents=True, exist_ok=True)
    # Based on number of 0-2 vowel combos
    vComboCount = countCombos(6, (0, 1, 2))
    # Based roughly on number of n-letter words
    maxCounts = {
        "1": 0,
        "2": 100 // vComboCount,
        "3": 500 // vComboCount,
        "*": 2000 // vComboCount,
        "7": 1000 // vComboCount,
        "8": 500 // vComboCount,
    }
    maxReps = {
        "1x": 0,
        "2x": 1,
        "3x": 1,
        "4x": 0,
        "5x": 0,
        "6x": 0,
    }
    minFreq = 1
    baseline = BASELINE

    files = FileHandler(eDir, oDir, minFreq, maxCounts, maxReps, baseline)
    files = toPangrams(files)
    files.finish()
