from whalrus.utils.Utils import cached_property, DeleteCacheMixin, NiceSet
from whalrus.rule.Rule import Rule


class Elimination(DeleteCacheMixin):
    """
    An elimination method.

    :param rule: if mentioned, will be passed to `__call__` immediately after initialization.

    A :class:`Elimination` object is a callable whose input is a rule (which has already loaded a profile). When the
    :class:`Elimination` object is called, it loads the rule. The output of the call is the :class:`Elimination` object
    itself. But after the call, you can access to the computed variables (ending with an underscore), such as
    :attr:`eliminated_` or :attr:`qualified_`.

    Cf. :class:`EliminationLast` for some examples.
    """

    def __init__(self, rule: Rule = None):
        """
        Remark: this `__init__` must always be called at the end of the subclasses' `__init__`.
        """
        # Computed variables
        self.rule_ = None
        # Optional: load a rule at initialization
        if rule is not None:
            self(rule=rule)

    def __call__(self, rule: Rule):
        self.rule_ = rule
        self.delete_cache()
        return self

    @cached_property
    def eliminated_order_(self) -> list:
        """
        The order on the eliminated candidates.

        :return: a list of :class:`NiceSet` objects. Each set represents a class of tied candidates. The first set in
            the list represents the `best' eliminated candidates, whereas the last set represent the `worst'
            candidates. Cf. :class:`EliminationLast` for some examples.
        """
        raise NotImplementedError

    @cached_property
    def eliminated_(self) -> NiceSet:
        """
        The eliminated candidates.

        :return: a :class:`NiceSet` of candidates.

        This should always be non-empty.
        """
        return NiceSet(c for tie_class in self.eliminated_order_ for c in tie_class)

    @cached_property
    def qualified_(self) -> NiceSet:
        """
        The candidates that are qualified (not eliminated).

        :return: a :class:`NiceSet` of candidates.
        """
        return NiceSet(self.rule_.candidates_ - self.eliminated_)