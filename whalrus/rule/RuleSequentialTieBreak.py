# -*- coding: utf-8 -*-
"""
Copyright Sylvain Bouveret, Yann Chevaleyre and François Durand
sylvain.bouveret@imag.fr, yann.chevaleyre@dauphine.fr, fradurand@gmail.com

This file is part of Whalrus.

Whalrus is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Whalrus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Whalrus.  If not, see <http://www.gnu.org/licenses/>.
"""
from whalrus.utils.Utils import cached_property, NiceSet
from whalrus.rule.Rule import Rule
from whalrus.rule.RulePlurality import RulePlurality
from whalrus.rule.RuleBorda import RuleBorda
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.priority.Priority import Priority
from typing import Union


class RuleSequentialTieBreak(Rule):
    """
    A rule by sequential tie-break.

    :param rules: a list of rules.

    Winner is determined by the first rule. If there is a tie, it is broken by the second rule. Etc. There may
    still be a tie at the end (which can be broken by the tie-breaking rule of this object).

    >>> plurality = RulePlurality()
    >>> borda = RuleBorda()
    >>> rule = RuleSequentialTieBreak(rules=[plurality, borda], tie_break=Priority.ASCENDING)
    >>> profile = Profile(
    ...     ['a > d > e > b > c', 'b > d > e > a > c', 'c > d > e > a > b',
    ...      'd > e > b > a > c', 'e > d > b > a > c'],
    ...     weights=[2, 2, 2, 1, 1]
    ... )
    >>> plurality(profile).gross_scores_ == {'a': 2, 'b': 2, 'c': 2, 'd': 1, 'e': 1}
    True
    >>> borda(profile).gross_scores_ == {'a': 14, 'b': 14, 'c': 8, 'd': 25, 'e': 19}
    True
    >>> rule(profile).order_ == [{'a', 'b'}, {'c'}, {'d'}, {'e'}]
    True
    >>> rule.winner_
    'a'
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, converter: ConverterBallot = None,
                 rules: list = None):
        self.rules = rules
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates,
            tie_break=tie_break, converter=converter
        )

    @cached_property
    def order_(self) -> list:
        orders = [rule(self.profile_converted_).order_ for rule in self.rules]
        # rank_tuples[a] will be (rank in order 0, rank in order 1, ...)
        rank_tuples = {c: [] for c in self.candidates_}
        for order in orders:
            for i, tie_class in enumerate(order):
                for c in tie_class:
                    rank_tuples[c].append(i)
        rank_tuples = {k: tuple(v) for k, v in rank_tuples.items()}
        # Now, sort by lexicographic order of "rank tuples"
        return [NiceSet(k for k in rank_tuples.keys() if rank_tuples[k] == v)
                for v in sorted(set(rank_tuples.values()))]

    # TODO: some methods such as cowinners_ might be overridden for a better performance.
