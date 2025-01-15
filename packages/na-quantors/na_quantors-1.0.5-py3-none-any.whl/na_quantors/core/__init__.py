from typing import *

import pandas as pd

__all__ = [
    "allisna",
    "allnotna",
    "anyisna",
    "anynotna",
    "isna",
    "notna",
]


def allisna(*values: Any) -> bool:
    "This function determines if all of the values are NaN."
    return all(isna(x) for x in values)


def allnotna(*values: Any) -> bool:
    "This function determines if all of the values are not NaN."
    return all(notna(x) for x in values)


def anyisna(*values: Any) -> bool:
    "This function determines if any of the values are NaN."
    return any(isna(x) for x in values)


def anynotna(*values: Any) -> bool:
    "This function determines if any of the values are not NaN."
    return any(notna(x) for x in values)


def isna(*values: Any) -> bool:
    "This function determines if the values are NaN."
    ans = {(pd.isna(x) is True) for x in values}
    (ans,) = ans
    return ans


def notna(*values: Any) -> bool:
    "This function determines if the values are not NaN."
    return not isna(*values)
