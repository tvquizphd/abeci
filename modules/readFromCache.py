import pickle
import yaml


def readLines(readableFile):
    print(f"Reading {readableFile}")
    if not readableFile.is_file():
        return []
    with open(readableFile, 'r') as rf:
        return rf.read().splitlines()


def writeLines(readableFile, lines):
    mode = 'a' if readableFile.is_file() else 'w'
    with open(readableFile, mode) as wf:
        for line in lines:
            wf.write(f"{line}\n")


def readFromCache(yamlFile, transform):
    pickleFile = yamlFile.with_suffix('.p')
    pickled = pickleFile.is_file()
    if pickled:
        with open(pickleFile, 'rb') as rf:
            print(f'Reading {pickleFile}...')
            return pickle.load(rf)

    with open(yamlFile, 'r') as rf:
        print(f'Reading {yamlFile}...')
        transformed = transform(yaml.safe_load(rf))
        if not pickled:
            print(f'Writing {pickleFile}')
            with open(pickleFile, "wb") as wf:
                pickle.dump(transformed, wf)
        return transformed
