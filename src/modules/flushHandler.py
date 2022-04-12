import logging

class FlushHandler():

    EMPTY_MAX = 100
    OUTPUT_MAX = 1000

    def __init__(self, flushEmpty=None, flushOutput=None):
        self._flushEmpty = flushEmpty
        self._flushOutput = flushOutput

    def flushEmpty(self, config):
        empty = config.empty
        emptyCount = len(empty)
        if self._flushEmpty and emptyCount >= self.EMPTY_MAX:
            logging.info(f'Flushing {emptyCount} empty patterns.')
            self._flushEmpty(config)
            return []
        return empty

    def flushOutput(self, config):
        output = config.output
        outputCount = len(output)
        if self._flushOutput and len(output) >= self.OUTPUT_MAX:
            logging.info(f'Flushing {outputCount} output patterns.')
            self._flushOutput(config)
            return []
        return output
