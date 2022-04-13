import logging
import pickle
import yaml


def readLines(readableFile):
    logging.info(f"Reading {readableFile}")
    if not readableFile.is_file():
        return []
    with open(readableFile, 'r') as rf:
        return rf.read().splitlines()


def writeLines(readableFile, lines):
    mode = 'a' if readableFile.is_file() else 'w'
    with open(readableFile, mode) as wf:
        for line in lines:
            wf.write(f"{line}\n")


def noChange(value):
    return value


def readFromCache(yamlFile, transform=None):
    transform = transform if transform else noChange
    pickleFile = yamlFile.with_suffix('.p')
    pickled = pickleFile.is_file()
    if pickled:
        with open(pickleFile, 'rb') as rf:
            logging.info(f'Reading {pickleFile}...')
            return pickle.load(rf)

    with open(yamlFile, 'r') as rf:
        logging.info(f'Reading {yamlFile}...')
        transformed = transform(yaml.safe_load(rf))
        if not pickled:
            logging.info(f'Writing {pickleFile}')
            with open(pickleFile, "wb") as wf:
                pickle.dump(transformed, wf)
        return transformed
