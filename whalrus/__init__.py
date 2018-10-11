# -*- coding: utf-8 -*-

"""Top-level package for Whalrus."""

__author__ = """Sylvain Bouveret, Yann Chevaleyre and François Durand"""
__email__ = 'fradurand@gmail.com'
__version__ = '0.1.0'

# Utils
from .utils.Utils import cached_property, DeleteCacheMixin, parse_weak_order, set_to_list, set_to_str, dict_to_items, \
    dict_to_str

# Scales
from .scales.Scale import Scale
from .scales.ScaleFromList import ScaleFromList
from .scales.ScaleFromSet import ScaleFromSet
from .scales.ScaleRange import ScaleRange
from .scales.ScaleInterval import ScaleInterval

# Priority
from .priority.Priority import Priority

# Ballots
from .ballots.Ballot import Ballot
from .ballots.BallotOrder import BallotOrder
from .ballots.BallotLevels import BallotLevels
from .ballots.BallotOneName import BallotOneName
from .ballots.BallotPlurality import BallotPlurality
from .ballots.BallotVeto import BallotVeto

# Ballot Converters
from .converters_ballot.ConverterBallot import ConverterBallot
from .converters_ballot.ConverterBallotGeneral import ConverterBallotGeneral
from .converters_ballot.ConverterBallotToPlurality import ConverterBallotToPlurality

# Examples of documentation
from .SubPackage1.MyClass1 import MyClass1
from .SubPackage2.MyClass2 import MyClass2
from .SubPackage2.MyClass3 import MyClass3
