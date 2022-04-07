import logging

FMT0 = "{message}"
FMT1 = "{levelname} - {message}"
HTTP = "Starting new HTTP connection (%d): %s:%s"
FMTK = {
    "style": "{"
}


def isNoEnd(record):
    endCode = ', '
    msg = str(record.msg)
    return any([msg[-2:] == endCode, msg == "."])


def isGoogleDebug(record):
    msg = str(record.msg)
    isDebug = record.levelno == 10
    return isDebug and any([
        msg == HTTP, msg[:7] == "%s://%s"
    ])


def updater(self, fmt0, fmt1, record):
    noEnd = isNoEnd(record)
    if isGoogleDebug(record):
        return False
    isHigh = record.levelno > 20
    self.setFormatter(fmt1 if isHigh else fmt0)
    if noEnd:
        self.terminator = ''
    else:
        self.terminator = '\n'
    return True


class StreamHandler(logging.StreamHandler):

    fmt0 = logging.Formatter(FMT0, **FMTK)
    fmt1 = logging.Formatter(FMT1, **FMTK)

    def emit(self, record):
        if updater(self, self.fmt0, self.fmt1, record):
            return super().emit(record)


class FileHandler(logging.FileHandler):

    fmt0 = logging.Formatter(FMT0, **FMTK)
    fmt1 = logging.Formatter(FMT1, **FMTK)

    def emit(self, record):
        if updater(self, self.fmt0, self.fmt1, record):
            return super().emit(record)


def makeHandler(filename=None):

    return FileHandler(filename) if filename else StreamHandler()
