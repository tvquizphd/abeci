from abeci.savePangrams import savePangrams
from abeci.arguments import Arguments

import logging


def pangramsCli():
    arguments = Arguments()
    args = arguments.list
    nArgs, nNeeded = len(args), Arguments.needed()
    if nArgs == nNeeded:
        pangramArgs = args[1:]
        shh = pangramArgs[2]
        if not shh:
            try:
                arguments.setLogging(args[0])
            except OSError as e:
                print(str(e))
        savePangrams(*pangramArgs)
    else:
        logging.error(f"Only {nArgs} of {nNeeded} args")
