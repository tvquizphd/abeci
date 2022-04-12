class FlushHandler():

    EMPTY_MAX = 100
    OUTPUT_MAX = 1000

    def __init__(self, flushEmpty=None, flushOutput=None):
        self._flushEmpty = flushEmpty
        self._flushOutput = flushOutput

    def flushEmpty(self, config):
        empty = config.empty
        if self._flushEmpty and len(empty) >= self.EMPTY_MAX:
            self._flushEmpty(config)
            return []
        return empty

    def flushOutput(self, config):
        output = config.output
        if self._flushOutput and len(output) >= self.OUTPUT_MAX:
            self._flushOutput(config)
            return []
        return output
