def flattenList(tree):
    if len(tree) == 0:
        return tree
    if isinstance(tree[0], list):
        return flattenList(tree[0]) + flattenList(tree[1:])
    return tree[:1] + flattenList(tree[1:])


def toLeafList(tree, empty):
    flat = flattenList(tree)
    leaves = [i for i in flat if i not in empty]
    return leaves + ['']


class Patterns():

    def __init__(self, tree, empty):
        self.tree = tree
        self.list = toLeafList(tree, empty)


def patternFunction(empty):
    def toPatterns(tree):
        return Patterns(tree, empty)
    return toPatterns
