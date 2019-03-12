from whalrus.rule.RuleScoreNum import RuleScoreNum
from whalrus.scorer.Scorer import Scorer
from whalrus.profile.Profile import Profile
from whalrus.priority.Priority import Priority
from whalrus.utils.Utils import cached_property, NiceDict
from whalrus.converter_ballot.ConverterBallot import ConverterBallot
from typing import Union
from numbers import Number


class RuleScoreNumAverage(RuleScoreNum):
    """
    A voting rule where a candidates's score is an average of the scores provided by the ballots

    :param scorer: the :class:`Scorer`. For each ballot, it is in charge of computing its contribution to each
        candidate's score.
    :param default_average: the default average score of a candidate when it receives no score whatsoever. It may
        happen, for example, if all voters abstain about this candidate. This avoids a division by zero when
        computing this candidate's average score.

    Cf. :class:`RuleRangeVoting`, etc for some examples.
    """

    def __init__(self, ballots: Union[list, Profile] = None, weights: list = None, voters: list = None,
                 candidates: set = None,
                 tie_break: Priority = Priority.UNAMBIGUOUS, converter: ConverterBallot = None,
                 scorer: Scorer = None, default_average: Number = 0.):
        self.scorer = scorer
        self.default_average = default_average
        super().__init__(
            ballots=ballots, weights=weights, voters=voters, candidates=candidates,
            tie_break=tie_break, converter=converter
        )

    @cached_property
    def _brute_scores_and_weights_(self) -> dict:
        brute_scores = NiceDict({c: 0 for c in self.candidates_})
        weights = NiceDict({c: 0 for c in self.candidates_})
        for ballot, weight, voter in self.profile_converted_.items():
            for c, value in self.scorer(ballot=ballot, voter=voter, candidates=self.candidates_).scores_.items():
                brute_scores[c] += weight * value
                weights[c] += weight
        return {'brute_scores': brute_scores, 'weights': weights}

    @cached_property
    def brute_scores_(self) -> NiceDict:
        """
        The brute scores for each candidate.

        :return: a dictionary. Key: candidate. Value: the sum of scores, multiplied by the weights of the
            corresponding voters. This is the numerator in the candidate's average score.
        """
        return self._brute_scores_and_weights_['brute_scores']

    @cached_property
    def weights_(self) -> NiceDict:
        """
        The weights for each candidate.

        :return: a dictionary. Key: candidate. Value: the total weight for this candidate, i.e. the total weight of all
            voters who assign a score to this candidate. This is the denominator in the candidate's average score.
        """
        return self._brute_scores_and_weights_['weights']

    @cached_property
    def scores_(self) -> NiceDict:
        return NiceDict({c: score / self.weights_[c] if self.weights_[c] > 0 else self.default_average
                         for c, score in self.brute_scores_.items()})
