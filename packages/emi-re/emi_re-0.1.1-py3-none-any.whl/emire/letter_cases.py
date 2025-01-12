import re


def to_snake_case(camel_case_str: str) -> str:
    """
    >>> to_snake_case("port")
    'port'
    >>> to_snake_case("gatherUsageStats")
    'gather_usage_stats'
    >>> to_snake_case("enforceSerializableSessionState")
    'enforce_serializable_session_state'
    >>> to_snake_case("showPyplotGlobalUse")
    'show_pyplot_global_use'
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_case_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
