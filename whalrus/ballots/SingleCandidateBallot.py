from whalrus.ballots.UtilityBallot import UtilityBallot
from toolz import first

class SingleCandidateBallot(UtilityBallot):

    @classmethod
    def create_plurality_ballot(cls,b):

        assert isinstance(b,UtilityBallot)

        biggest_val  = max(b.values())
        arg_maxs     = [c for c,v in b.items() if v==biggest_val]

        if len(arg_maxs) > 1:
            raise Exception('Failed to convert ballot to plurality ballot because many candidates have the same score')

        return SingleCandidateBallot( first(arg_maxs) , weight=self.weight )


    def candidate(self):
        return first(self.keys())


