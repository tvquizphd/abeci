from .readWordRecords import readWordRecords
from .defaults import normalizeArguments
from .listPatterns import listPatterns
from .logHandler import StreamHandler
from .fileHandler import FileHandler
from .typo.loadTypos import loadTypos
from .toPangrams import toPangrams
from .listMaps import listMaps
from .defaults import Defaults
from .config import Config

from pathlib import Path
import logging


def makeConfig(shh, *args):
    return Config(shh, *normalizeArguments(*args))


def loadLoop(files):
    try:
        loop = files.readLoop()
    except FileNotFoundError as e:
        logging.info("Loading word loop, ")
        logging.warning(e)
        loop = readWordRecords()
    return loop


def savePangrams(oDir, eDir, *configArguments):
    log_ = {
        "handlers": [StreamHandler()],
        "encoding": "utf-8",
        "level": "INFO",
    }
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(**log_)

    oDir = oDir if oDir else Defaults.oDir
    eDir = eDir if eDir else Defaults.eDir

    oDir.mkdir(parents=True, exist_ok=True)
    eDir.mkdir(parents=True, exist_ok=True)

    config = makeConfig(*configArguments)
    thisFolder = Path(__file__).parent.absolute()
    typoDataFolder = thisFolder / Path("typo", "data")
    typos = loadTypos(typoDataFolder)
    files = FileHandler(eDir, oDir, config)
    config = files.readEmptyFile()
    # Try to read existing files
    try:
        maps = files.readMaps()
    except FileNotFoundError as e:
        logging.info("Loading word maps, ")
        logging.warning(e)
        loop = loadLoop(files)
        maps = listMaps(loop, typos, config)
        files.writeMaps(maps)
        files.finishLoop(config)
    try:
        patterns = files.readPatterns()
    except FileNotFoundError as e:
        logging.info("Loading word patterns, ")
        logging.warning(e)
        patterns = listPatterns(maps, config)
        files.writePatterns(patterns)

    # Generate the actual pangrams
    try:
        config = toPangrams(maps, patterns, config)
    except KeyboardInterrupt:
        files.exit()
    files.finish(config, done=True)
