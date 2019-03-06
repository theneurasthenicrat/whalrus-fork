from whalrus.utils.Utils import cached_property
from whalrus.rule.Rule import Rule
from whalrus.rule.RulePlurality import RulePlurality
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.priority.Priority import Priority
from whalrus.elimination.Elimination import Elimination
from whalrus.elimination.EliminationLast import EliminationLast
from typing import Union
from copy import deepcopy
from itertools import chain


class RuleIteratedElimination(Rule):
    """
    A rule by sequential elimination (such as IRV, Coombs, Baldwin, Nanson...)

    :param base_rule: the rule used at each round to determine the trailing candidate.
    :param elimination: the elimination algorithm. Default: ``EliminationLast(k=1)``.
    :param propagate_tie_break: if True (default), then the tie-breaking rule of this object is also used for the
        base rule.

    >>> irv = RuleIteratedElimination(['a > b > c', 'b > a > c', 'c > a > b'], weights=[2, 3, 4],
    ...                                 base_rule=RulePlurality())
    >>> irv.eliminations_[0].rule_.scores_
    {'a': 2, 'b': 3, 'c': 4}
    >>> irv.eliminations_[1].rule_.scores_
    {'b': 5, 'c': 4}
    >>> irv.eliminations_[2].rule_.scores_
    {'b': 9}
    >>> irv.winner_
    'b'

    By default, ``propagate_tie_break`` is True. So if you want to specify a tie-breaking rule, just do it in the
    parameters of this object, and it will also be used in the base rule:

    >>> irv = RuleIteratedElimination(['a > c > b', 'b > a > c', 'c > a > b'], weights=[1, 2, 1],
    ...                                 base_rule=RulePlurality(), tie_break=Priority.ASCENDING)
    >>> irv.eliminations_[0].rule_.scores_
    {'a': 1, 'b': 2, 'c': 1}
    >>> irv.eliminations_[1].rule_.scores_
    {'a': 2, 'b': 2}
    >>> irv.eliminations_[2].rule_.scores_
    {'a': 4}
    >>> irv.winner_
    'a'

    If ``propagate_tie_break`` is False, then there is a subtlety between the tie-breaking rule of this object, and the
    tie-breaking rule of the base rule. The following (somewhat contrived) example illustrates the respective roles of
    the two tie-breaking rules.

    >>> rule = RuleIteratedElimination(
    ...     ['a', 'b', 'c', 'd', 'e'], weights=[3, 2, 2, 2, 1],
    ...     tie_break=Priority.DESCENDING, propagate_tie_break=False,
    ...     base_rule=RulePlurality(tie_break=Priority.ASCENDING), elimination=EliminationLast(k=2))
    >>> rule.eliminations_[0].rule_.scores_
    {'a': 3, 'b': 2, 'c': 2, 'd': 2, 'e': 1}

    With the worst score, ``e`` is eliminated anyway, but we need to eliminate a second candidate because ``k = 2``. In
    Plurality, ``b``, ``c`` and ``d`` are tied, but since Plurality's tie-breaking rule is ``ASCENDING``, candidates
    ``b`` or ``c`` get an advantage over ``d``. Hence ``d`` is eliminated:

    >>> rule.eliminations_[0].eliminated_
    {'d', 'e'}

    Finally, the tie-breaking rule of the base rule (here Plurality) is always sufficient to compute the weak order over
    the candidates. Note that this order is finer than the elimination order, because being eliminated at the same
    time does not mean being tied, as ``d`` and ``e`` illustrate here:

    >>> rule.order_
    [{'a'}, {'b', 'c'}, {'d'}, {'e'}]

    So, where does the tie-breaking rule of this object come in? It is simply used to get the strict order over
    the candidates, as usual in a :class:`Rule`. In our example, since it is ``DESCENDING``, candidate ``c`` gets an
    advantage over ``b``:

    >>> rule.strict_order_
    ['a', 'c', 'b', 'd', 'e']
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None, converter: ConverterBallot = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, default_converter: ConverterBallot = None,
                 base_rule: Rule = None, elimination: Elimination = None, propagate_tie_break=True):
        if elimination is None:
            elimination = EliminationLast(k=1)
        self.base_rule = base_rule
        self.elimination = elimination
        self.propagate_tie_break = propagate_tie_break
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates, converter=converter,
            tie_break=tie_break, default_converter=default_converter
        )

    def _check_profile(self, candidates: set) -> None:
        # We delegate this task to the base rule.
        pass

    @cached_property
    def eliminations_(self) -> list:
        """
        The elimination rounds.

        :return: a list of :class:`Elimination` objects. The first one corresponds to the first round, etc.
        """
        self.elimination.delete_cache()
        self.base_rule.delete_cache()
        eliminations = []
        candidates = self.candidates_
        while candidates:
            elimination = deepcopy(self.elimination)
            rule = deepcopy(self.base_rule)
            if self.propagate_tie_break:
                rule.tie_break = self.tie_break
            rule(ballots=self.profile_converted_, candidates=candidates)
            elimination(rule=rule)
            eliminations.append(elimination)
            candidates = elimination.qualified_
        return eliminations

    @cached_property
    def order_(self) -> list:
        return list(chain(*[elimination.eliminated_order_ for elimination in self.eliminations_[::-1]]))