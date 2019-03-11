from whalrus.scale.ScaleRange import ScaleRange
from whalrus.rule.RuleRangeVoting import RuleRangeVoting
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.converter_ballot.ConverterBallotToGrades import ConverterBallotToGrades
from whalrus.priority.Priority import Priority
from whalrus.profile.Profile import Profile
from typing import Union
import numbers


class RuleApproval(RuleRangeVoting):
    """
    Approval voting.

    :param default_converter: the default is ``ConverterBallotToGrades(scale=ScaleRange(0, 1))``.

    Cf. :class:`RulePlurality` and :class:`Rule` for the general syntax.

    >>> RuleApproval([{'a': 1, 'b': 0, 'c': 0}, {'a': 1, 'b': 1, 'c': 0}]).scores_
    {'a': 1.0, 'b': 0.5, 'c': 0.0}

    With ballot conversion:

    >>> RuleApproval(['a > b > c > d', 'c > a > b > d']).scores_
    {'a': 1.0, 'b': 0.5, 'c': 0.5, 'd': 0.0}
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None, tie_break: Priority = Priority.UNAMBIGUOUS,
                 default_converter: ConverterBallot = None):
        if default_converter is None:
            default_converter = ConverterBallotToGrades(scale=ScaleRange(0, 1))
        super().__init__(ballots=ballots, weights=weights, voters=voters, candidates=candidates, tie_break=tie_break,
                         default_converter=default_converter)
