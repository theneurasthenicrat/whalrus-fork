from pyparsing import Group, Word, ZeroOrMore, alphas, nums, ParseException
from toolz import merge

def parse_weak_order(s):
    """
    Converts a string representing a weak-order to a dictionary
    Throws a 'ParseException' if the string is not a valid weak-order

    Example:

    >>> s = 'Jean ~ Titi ~ tata32 > moi > toi ~ nous > eux'
    >>> parse_weak_order(s)
    {'Jean': 3, 'Titi': 3, 'tata32': 3, 'moi': 2, 'toi': 1, 'nous': 1, 'eux': 0}

    Another example.
    Here, an exception is thrown because the string is not a valid weak-order:

    >>> try:
    ...    parse_weak_order('a * b')
    ... except ParseException:
    ...    print('invalid')
    invalid

    """

    candidate = Word(alphas.upper() + alphas.lower() + nums + '_')
    equiv_class = Group(candidate + ZeroOrMore(Word('~').suppress() + candidate))
    weakpref = equiv_class + ZeroOrMore(Word('>').suppress() + equiv_class)

    # if s = 'Jean ~ Titi ~ tata32 > moi > toi ~ nous > eux', then
    # parsed = [['Jean', 'Titi', 'tata32'], ['moi'], ['toi', 'nous'], ['eux']]
    parsed = weakpref.parseString(s, parseAll=True).asList()

    lst = []
    for v, t in enumerate(reversed(parsed)):
        lst = [(c, v) for c in t] + lst

    return dict(lst)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
