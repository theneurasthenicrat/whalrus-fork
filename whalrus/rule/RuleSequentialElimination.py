from whalrus.utils.Utils import cached_property
from whalrus.rule.Rule import Rule
from whalrus.rule.RuleBorda import RuleBorda
from whalrus.rule.RulePlurality import RulePlurality
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.priority.Priority import Priority
from whalrus.elimination.Elimination import Elimination
from whalrus.elimination.EliminationLast import EliminationLast
from whalrus.elimination.EliminationBelowAverage import EliminationBelowAverage
from typing import Union
from copy import deepcopy
from itertools import chain


class RuleSequentialElimination(Rule):
    # noinspection PyUnresolvedReferences
    """
    A rule by sequential elimination (such as the Two-Round System).

    :param rules: the list of rules, one for each round.
    :param eliminations: the list of elimination rounds, one for each round except the last one.
    :param propagate_tie_break: if True (default), then the tie-breaking rule of this object is also used for the
        base rules. Cf. :class:`RuleIteratedElimination` for more explanation on this parameter.

    >>> rule = RuleSequentialElimination(
    ...     ['a > b > c > d > e', 'b > c > d > e > a'], weights=[2, 1],
    ...     rules=[RuleBorda(), RulePlurality(), RulePlurality()],
    ...     eliminations=[EliminationBelowAverage(), EliminationLast(k=1)])
    >>> rule.elimination_rounds_[0].rule_.scores_
    {'a': 8.0, 'b': 10.0, 'c': 7.0, 'd': 4.0, 'e': 1.0}
    >>> rule.elimination_rounds_[1].rule_.scores_
    {'a': 2, 'b': 1, 'c': 0}
    >>> rule.final_round_.scores_
    {'a': 2, 'b': 1}

    If ``rules`` is not a list, the number of rounds is inferred from ``eliminations``. An application of this is to
    define the two-round system:

    >>> rule = RuleSequentialElimination(
    ...     ['a > b > c > d > e', 'b > a > c > d > e', 'c > a > b > d > e'], weights=[2, 2, 1],
    ...     rules=RulePlurality(), eliminations=[EliminationLast(k=-2)])
    >>> rule.elimination_rounds_[0].rule_.scores_
    {'a': 2, 'b': 2, 'c': 1, 'd': 0, 'e': 0}
    >>> rule.final_round_.scores_
    {'a': 3, 'b': 2}

    Note: there exists a shortcut for this rule in particular, the class :class:`RuleTwoRound`.

    Conversely, if ``elimination`` is not a list, the number of rounds is deduced from ``rules``:

    >>> rule = RuleSequentialElimination(
    ...     ['a > b > c > d > e', 'b > a > c > d > e'], weights=[2, 1],
    ...     rules=[RuleBorda(), RuleBorda(), RulePlurality()], eliminations=EliminationLast(k=1))
    >>> rule.elimination_rounds_[0].rule_.scores_
    {'a': 11.0, 'b': 10.0, 'c': 6.0, 'd': 3.0, 'e': 0.0}
    >>> rule.elimination_rounds_[1].rule_.scores_
    {'a': 8.0, 'b': 7.0, 'c': 3.0, 'd': 0.0}
    >>> rule.final_round_.scores_
    {'a': 2, 'b': 1, 'c': 0}
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None, tie_break: Priority = Priority.UNAMBIGUOUS,
                 default_converter: ConverterBallot = None):
        # Default values
        if eliminations is None:
            eliminations = EliminationLast(k=1)
        # Deal with the polymorphism of the definition
        if isinstance(rules, list):
            n_rounds = len(rules)
        elif isinstance(eliminations, list):
            n_rounds = len(eliminations) + 1
        else:
            n_rounds = 1
        if isinstance(rules, Rule):
            rules.delete_cache()
            rules = [deepcopy(rules) for _ in range(n_rounds)]
        if isinstance(eliminations, Elimination):
            eliminations.delete_cache()
            eliminations = [deepcopy(eliminations) for _ in range(n_rounds - 1)]
        # Record variables and initialize
        self.rules = rules
        self.eliminations = eliminations
        self.propagate_tie_break = propagate_tie_break
        super().__init__(ballots=ballots, weights=weights, voters=voters, candidates=candidates, tie_break=tie_break,
                         default_converter=default_converter)

    def _check_profile(self, candidates: set) -> None:
        # We delegate this task to the base rules.
        pass

    @cached_property
    def rounds_(self) -> list:
        # noinspection PyUnresolvedReferences
        """
        The rounds.

        :return: a list. All rounds but the last one are :class:`Elimination` objects. The last one is a :class:`Rule`
            object.

        Note that in some cases, there may be fewer actual rounds than declared in the definition of the rule:

        >>> rule = RuleSequentialElimination(['a > b > c > d', 'a > c > d > b', 'a > d > b > c'])
        >>> len(rule.rounds_)
        2
        >>> rule.elimination_rounds_[0].rule_.scores_
        {'a': 9.0, 'b': 3.0, 'c': 3.0, 'd': 3.0}
        >>> rule.final_round_.scores_
        {'a': 3}
        """
        rounds = []
        candidates = self.candidates_
        for i, elimination in enumerate(self.eliminations):
            rule = self.rules[i]
            if self.propagate_tie_break:
                rule.tie_break = self.tie_break
            rule(ballots=self.profile_converted_, candidates=candidates)
            elimination(rule=rule)
            candidates = elimination.qualified_
            if candidates:
                rounds.append(elimination)
            else:
                rounds.append(rule)
                break
        else:
            rule = self.rules[-1]
            if self.propagate_tie_break:
                rule.tie_break = self.tie_break
            rule(ballots=self.profile_converted_, candidates=candidates)
            rounds.append(rule)
        return rounds

    @cached_property
    def elimination_rounds_(self) -> list:
        """
        The elimination rounds.

        :return: a list of :class:`Elimination` objects. All rounds except the last one.
        """
        return self.rounds_[:-1]

    @cached_property
    def final_round_(self) -> Rule:
        """
        The final round.

        :return: a :class:`Rule` object. The last round, which decides the winner of the election.
        """
        return self.rounds_[-1]

    @cached_property
    def order_(self) -> list:
        return (self.final_round_.order_ +
                list(chain(*[elimination.eliminated_order_ for elimination in self.elimination_rounds_[::-1]])))