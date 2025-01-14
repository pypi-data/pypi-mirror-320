from typing import Any, Dict


def dict_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """merge two dict recursively and return a new merged dict
    1. if two nodes in the same position are both dicts,
       merge is recursively,
    2. if two nodes in the same position are not both dicts,
       value from the second one overwrites one in first.

    Args:
        a (dict): first dict
        b (dict): second dict

    Returns:
        dict: a new merged dict
    """
    merged = dict()
    for k in set(a.keys()).union(b.keys()):
        if (k in a) and (k in b):
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                merged[k] = dict_merge(a[k], b[k])
            else:
                merged[k] = b[k]
        elif k in a:
            merged[k] = a[k]
        else:  # k in b
            merged[k] = b[k]
    return merged
