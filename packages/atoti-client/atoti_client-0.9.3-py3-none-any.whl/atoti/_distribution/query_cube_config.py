from collections.abc import Set as AbstractSet
from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._identification import ClusterName
from .._ipython import ReprJson, ReprJsonable
from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class QueryCubeConfig(ReprJsonable):
    cluster: ClusterName

    # Consider changing this to `FrozenSequence[LevelKey]`.
    distribution_levels: AbstractSet[str] = frozenset()

    application_names: AbstractSet[str]

    catalog_names: AbstractSet[str] = frozenset(["atoti"])

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {
                "cluster": self.cluster,
                "distribution_levels": self.distribution_levels,
                "application_names": self.application_names,
            },
            {"expanded": False, "root": "QueryCubeConfig"},
        )
