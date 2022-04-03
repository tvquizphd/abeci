from modules.fileHandler import FileHandler
from modules.toPangrams import toPangrams

from pathlib import Path

if __name__ == "__main__":
    eDir = Path("effects")
    oDir = Path("results")
    maxima = [4, 120, 360, 1000]
    eDir.mkdir(parents=True, exist_ok=True)
    oDir.mkdir(parents=True, exist_ok=True)
    # Track given number of words by length

    files = FileHandler(eDir, oDir, maxima)
    files = toPangrams(files)
    files.finish()
