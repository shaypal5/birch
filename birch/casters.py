"""Custom env var value casters for birch."""


def true_false_caster(val):
    """Casts 'TRUE', 'true', etc. to True, all other strings to False."""
    if isinstance(val, bool):
        return val
    try:
        return val.lower() == 'true'
    except AttributeError:
        raise ValueError(f"Bad value {val} attempted to cast to bool!")
