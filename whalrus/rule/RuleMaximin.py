from whalrus.rule.RuleScore import RuleScore
from whalrus.priority.Priority import Priority
from whalrus.converter_ballot.ConverterBallotToOrder import ConverterBallotToOrder
from whalrus.utils.Utils import cached_property, NiceDict
from whalrus.profile.Profile import Profile
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from whalrus.matrix.Matrix import Matrix
from whalrus.matrix.MatrixWeightedMajority import MatrixWeightedMajority
from typing import Union


class RuleMaximin(RuleScore):
    """
    Maximin rule.

    :param matrix_weighted_majority: a :class:`Matrix`.

    The score of a candidate is the minimal non-diagonal coefficient on its raw of the matrix.

    >>> rule = RuleMaximin(ballots=['a > b > c', 'b > c > a', 'c > a > b'], weights=[4, 3, 3])
    >>> rule.matrix_weighted_majority_.as_df_
         a    b    c
    a  0.0  0.7  0.4
    b  0.3  0.0  0.7
    c  0.6  0.3  0.0
    >>> rule.scores_
    {'a': 0.4, 'b': 0.3, 'c': 0.3}
    >>> rule.winner_
    'a'
    """

    def __init__(self, ballots: Union[list, Profile]=None, weights: list=None, voters: list=None,
                 candidates: set=None, converter: ConverterBallot=None,
                 tie_break: Priority=Priority.UNAMBIGUOUS,
                 default_converter: ConverterBallot = ConverterBallotToOrder(),
                 matrix_weighted_majority: Matrix = MatrixWeightedMajority()):
        self.matrix_weighted_majority = matrix_weighted_majority
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates, converter=converter,
            tie_break=tie_break, default_converter=default_converter
        )

    @cached_property
    def matrix_weighted_majority_(self):
        """
        The weighted majority matrix.

        :return: the weighted majority matrix (once computed with the given profile).
        """
        return self.matrix_weighted_majority(self.profile_converted_)

    @cached_property
    def scores_(self) -> NiceDict:
        matrix = self.matrix_weighted_majority_
        return NiceDict({c: min({v for (i, j), v in matrix.as_dict_.items() if i == c and j != c})
                         for c in matrix.candidates_})
