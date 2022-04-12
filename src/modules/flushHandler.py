class FlushHandler():

    EMPTY_MAX = 100
    OUTPUT_MAX = 1000

    def __init__(self, flushEmpty=None, flushOutput=None):
        self.flushEmpty = flushEmpty
        self.flushOutput = flushOutput

    def flushEmpty(self, config):
        empty = config.empty
        if self.flushEmpty and len(empty) >= self.EMPTY_MAX:
            self.flushEmpty(config)
            return []
        return empty

    def flushOutput(self, config):
        output = config.output
        if self.flushOutput and len(output) >= self.OUTPUT_MAX:
            self.flushOutput(config)
            return []
        return output
