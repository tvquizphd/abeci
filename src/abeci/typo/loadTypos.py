import re
'''
    Commonly Misspelled English words stored into json.
    Corpora attained from Roger Milton's hompage
    https://www.dcs.bbk.ac.uk/~ROGER/corpora.html
'''
pattern = re.compile(r'\<ERR(.*?)\</ERR>')


def loadTypos(dataDir):
    # Birbeck misspellings
    birkbeck_file = open(dataDir / 'missp.dat.txt')
    birkbeck_data = birkbeck_file.readlines()

    # Holbrook misspellings
    holbrook_file = open(dataDir / 'holbrook-tagged.dat.txt')
    holbrook_data = holbrook_file.readlines()

    # Aspell misspellings
    aspell_file = open(dataDir / 'aspell.dat.txt')
    aspell_data = aspell_file.readlines()

    # Wikipedia misspellings
    wikipedia_file = open(dataDir / 'wikipedia.dat.txt')
    wikipedia_data = wikipedia_file.readlines()

    misspellings = set()

    def store_misspellings(data, misspellings):
        for data_line in data:
            if '$' not in data_line:
                mis_spell = data_line.strip()
                misspellings.add(mis_spell.lower())

    for data_line in holbrook_data:
        for match in pattern.finditer(data_line):
            split = match.groups()[0].split('> ')
            misspell = split[1].strip().lower()

            if misspell not in misspellings:
                misspellings.add(misspell)

    store_misspellings(birkbeck_data, misspellings)
    store_misspellings(aspell_data, misspellings)
    store_misspellings(wikipedia_data, misspellings)

    return misspellings
