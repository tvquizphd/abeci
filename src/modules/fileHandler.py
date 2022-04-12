from .readFromCache import readFromCache
from .readFromCache import writeLines
from .readFromCache import readLines
from .flushHandler import FlushHandler
from .patterns import patternFunction
from .maps import mapFunction

import logging
import pickle
import errno
import yaml
import sys
import os

noEnt = errno.ENOENT, os.strerror(errno.ENOENT)


def fileNotFound(filename):
    args = noEnt + (str(filename),)
    return FileNotFoundError(*args)


class FileHandler:

    def __init__(self, eDir, oDir, config):

        self.config = config
        toPath = self.config.toPath
        try:
            self.config.makeFolders([eDir, oDir])
        except ValueError as e:
            logging.error(e)
        self.patternFile = eDir / toPath("pattern", "yaml")
        self.wordFile = eDir / toPath("word", "yaml")
        self.emptyFile = eDir / toPath("empty", "txt")
        self.outFile = oDir / toPath("pangrams", "txt")
        self.sourceFile = eDir / "source.p"
        # Modify the config state
        flushEmpty = self.flushEmpty
        flushOutput = self.flushOutput
        self.config.flushHandler = FlushHandler(flushEmpty, flushOutput)

    def readEmptyFile(self):
        emptyFile = self.emptyFile
        if emptyFile.is_file():
            logging.info(f'Existing {emptyFile}')
            self.config.setEmpty(readLines(emptyFile))
            return self.config
        return self.config

    def writeLoop(self, source):
        sourceFile = self.sourceFile
        if sourceFile.is_file():
            logging.info(f'Existing {sourceFile}')
            return
        logging.info(f'Writing {sourceFile}')
        with open(sourceFile, "wb") as wf:
            pickle.dump(source, wf)

    def readLoop(self):
        sourceFile = self.sourceFile
        if not sourceFile.is_file():
            raise fileNotFound(sourceFile)
        with open(sourceFile, "rb") as rf:
            return pickle.load(rf)

    def writeMaps(self, maps):
        wordFile = self.wordFile
        wsMap = maps.wsMap
        if wordFile.is_file():
            logging.info(f'Existing {wordFile}')
            return
        logging.info(f'Writing {wordFile}')
        with open(wordFile, "w") as wf:
            yaml.dump(wsMap, wf)

    def readMaps(self):
        wordFile = self.wordFile
        if not wordFile.is_file():
            raise fileNotFound(wordFile)
        toMaps = mapFunction(self.config)
        return readFromCache(wordFile, toMaps)

    def writePatterns(self, patterns):
        tree = patterns.tree
        patternFile = self.patternFile
        if patternFile.is_file():
            logging.info(f'Existing {patternFile}')
            return
        logging.info(f'Writing {patternFile}')
        with open(patternFile, "w") as wf:
            yaml.dump(tree, wf)

    def readPatterns(self):
        patternFile = self.patternFile
        if not patternFile.is_file():
            raise fileNotFound(patternFile)
        empty = self.config.empty
        toPatterns = patternFunction(empty)
        return readFromCache(patternFile, toPatterns)

    def exit(self):
        try:
            self.finish(self.config, done=False)
        except (BrokenPipeError, IOError):
            pass
        sys.exit(0)

    def finishLoop(self, config):
        source = config.source
        self.writeLoop(source)
        sText = f"{len(source)} source words"
        logging.info(f'Saved {sText} to {self.sourceFile}')

    def flushOutput(self, config):
        self.config = config
        output = config.output
        writeLines(self.outFile, output)
        oText = f"{len(output)} perfect pangram sets"
        logging.info(f'Saved {oText} to {self.outFile}')

    def flushEmpty(self, config):
        self.config = config
        empty = config.empty
        writeLines(self.emptyFile, empty)
        eText = f"{len(empty)} unused patterns"
        logging.info(f'Saved {eText} to {self.emptyFile}')

    def finish(self, config, done=True):
        self.flushEmpty(config)
        self.flushOutput(config)
        if not done:
            logging.warning("Incomplete!")
        else:
            logging.info("Complete!")
