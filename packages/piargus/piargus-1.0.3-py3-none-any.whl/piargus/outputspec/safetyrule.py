from typing import Union, Collection, Sequence, Mapping, TypedDict


def safety_rule(code, maximum=None, dummy=None):
    """
    Decorator to add metadata to safety rule.

    A safety rule is a function returning a string.
    Because of how the batch api works some metadata is useful.

    :param code: Code used by batch file
    :param maximum: How often the rule can be applied. The rule can be used this many times
    on the individual level and this many times on the holding level.
    :param dummy: If the rule can be set on holding level, use dummy to fill individual level slots.
    """
    def accept_function(safety_function):
        safety_function.code = code
        safety_function.maximum = maximum
        safety_function.dummy = dummy
        return safety_function

    return accept_function


@safety_rule("NK", maximum=2, dummy="NK(0, 0)")
def dominance_rule(n=3, k=75):
    """
    (N, K)-dominance rule.

    n is the number of contributors to a cell contributing more than k% of the total value of the cel"""
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= k <= 100):
        raise ValueError("k should be a percentage")

    return f"NK{n, k}"


@safety_rule("P", maximum=2, dummy="P(0, 0)")
def percent_rule(p=10, n=1):
    """
    P%-rule.

    if x1 can be determined to an accuracy of better than p% of
    the true value then it is disclosive where x1 is the largest contributor to a cell."""
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= p <= 100):
        raise ValueError("p should be a percentage")

    return f"P{p, n}"


@safety_rule("FREQ", maximum=1, dummy="FREQ(0, 0)")
def frequency_rule(n, safety_range):
    """Frequency rule."""
    if n < 1:
        raise ValueError("n should be positive")
    if not (0 <= safety_range <= 100):
        raise ValueError("safety_range should be a percentage")

    return f"FREQ{n, safety_range}"


@safety_rule("REQ", maximum=1, dummy="REQ(0, 0, 0)")
def request_rule(percent1, percent2, safety_margin):
    """Request rule

    Here, cells are protected only when the largest contributor represents
    over (for example) 70% of the total and that contributor asked for protection.
    Therefore, a variable indicating the request is required
    """
    if not (0 <= percent1 <= 100):
        raise ValueError("percent1 should be a percentage")
    if not (0 <= percent2 <= 100):
        raise ValueError("percent2 should be a percentage")

    return f"REQ{percent1, percent2, safety_margin}"


@safety_rule("ZERO", maximum=1)
def zero_rule(safety_range):
    """Zero rule

    Whether zero-values are safe.
    """
    pass  # TODO Unclear from manual how to use safety_range and what to check
    return f"ZERO({safety_range})"


@safety_rule("MIS")
def missing_rule(is_safe=False):
    """Missing values rule

    Whether missing values are safe.
    """
    return f"MIS({int(is_safe)})"


@safety_rule("WGT")
def weight_rule(apply_weights=False):
    """Whether weights should be used in the safety rules."""
    return f"WGT({int(apply_weights)})"


@safety_rule("MAN")
def manual_rule(margin=20):
    """Manual rule

    A manually supplied safety range
    """
    if not (0 <= margin <= 100):
        raise ValueError("margin should be a percentage")

    return f"MAN({margin})"


RULES = [
    dominance_rule,
    percent_rule,
    frequency_rule,
    request_rule,
    zero_rule,
    missing_rule,
    weight_rule,
    manual_rule,
]

# Aliases for consistency with τ-argus-api
nk_rule = dominance_rule
p_rule = percent_rule


class SafetyRule(TypedDict, total=False):
    individual: Union[str, Collection[str]]
    holding: Union[str, Collection[str]]


def make_safety_rule(
    rule: Union[str, Collection[str], SafetyRule] = "", /,
    *,
    individual: Union[str, Collection[str]] = "",
    holding: Union[str, Collection[str]] = "",
) -> str:
    """
    Construct a safety rule from individual and holding parts.

    Dummy elements are inserted when necessary.
    """
    if rule:
        if individual or holding:
            raise TypeError("Function should either be called with 1 positional "
                            "or 2 keyword arguments.")
        elif isinstance(rule, str):
            return rule
        elif isinstance(rule, Mapping):
            return make_safety_rule(**rule)
        else:
            return "|".join(_split_rule(rule))

    if isinstance(individual, str):
        individual = _split_rule(individual)
    if isinstance(holding, str):
        holding = _split_rule(holding)

    dummy = []
    for rule in RULES:
        individual_count = sum(1 for part in individual if part.startswith(rule.code))
        holding_count = sum(1 for part in holding if part.startswith(rule.code))

        if rule.maximum:
            if max(individual_count, holding_count) > rule.maximum:
                raise ValueError(f"Rule {rule.code} can only appear {rule.maximum} times.")
            elif rule.dummy and holding_count > 0:
                n_dummies = rule.maximum - individual_count
                dummy.extend(n_dummies * [rule.dummy])

    safety_rule_list = list(individual) + dummy + list(holding)
    return "|".join(safety_rule_list)


def _split_rule(rule: Union[str, Collection[str]]) -> Sequence[str]:
    """
    Split a safety rule into parts.

    >>> _split_rule(["P(1)|NK(3, 7)", "FREQ(1)|NK(3, 7)", "ZERO(5)", [" P(1,2)", "MIS(1) "]])
    ['P(1)', 'NK(3, 7)', 'FREQ(1)', 'NK(3, 7)', 'ZERO(5)', 'P(1,2)', 'MIS(1)']
    """
    if isinstance(rule, str):
        return [part.strip() for part in rule.split("|") if part]
    else:
        return [part for subrule in rule for part in _split_rule(subrule)]
