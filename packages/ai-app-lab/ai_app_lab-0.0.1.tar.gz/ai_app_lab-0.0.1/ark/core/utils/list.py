from typing import Any, Dict, List, Optional


def list_item_merge(
    a: List[Dict[str, Any]], b: List[Dict[str, Any]], unique_key: Optional[str]
) -> List[Dict[str, Any]]:
    """
    merge two list items into a new one
    will use unique_key to identify the item
    """
    if not unique_key:
        return a + b

    merged = []
    unique_dict = {bb.get(unique_key, ""): bb for bb in b}
    for item in a:
        if item.get(unique_key, "") not in unique_dict.keys():
            merged.append(item)

    merged += b

    return merged
