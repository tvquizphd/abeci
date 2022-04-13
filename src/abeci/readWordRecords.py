from google_ngram_downloader import readline_google_store
import unidecode


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
            continue
        for record in records:
            if record.year == 2008:
                word = unidecode.unidecode(record.ngram)
                if isWordOkay(word):
                    frequency = record.match_count
                    yield [word.lower(), frequency]
