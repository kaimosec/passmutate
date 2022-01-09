import itertools


class Combinator:
    """
    For list:
    [
        ['a', 'b', 'c'],
        ['d'],
        ['e', 'f']
    ]
    Iterate through all possible combinations of all possible lengths and orders but avoiding elements
    grouped together from being in a combination together:
    ['a'],
    ['a', 'd'],
    ['a', 'f'],
    ['a', 'd', 'f']
    ...
    ['f', 'a'],
    ...
    ['e', 'd', 'c']
    """
    @staticmethod
    def getpossibilities(lst):
        for i in range(1, len(lst) + 1):
            for combo in itertools.permutations(lst, i):
                pools = [tuple(pool) for pool in combo]
                result = [[]]
                for pool in pools:
                    result = [x + [y] for x in result for y in pool]
                for prod in result:
                    yield prod
