from __future__ import annotations

from typing import Literal

from ._constant import Constant
from ._identification import HierarchyIdentifier, LevelIdentifier, MeasureIdentifier
from ._operation import Condition, ConditionComparisonOperatorBound

QueryFilter = Condition[
    HierarchyIdentifier | LevelIdentifier | MeasureIdentifier,
    ConditionComparisonOperatorBound,
    Constant | None,
    Literal["and"] | None,
]
