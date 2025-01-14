from collections.abc import Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._atoti_client import AtotiClient
from .._check_named_object_defined import check_named_object_defined
from .._identification import CubeIdentifier
from .._ipython import ReprJson, ReprJsonable
from .._java_api import JavaApi
from .._live_extension_unavailable_error import LiveExtensionUnavailableError
from ..aggregates_cache import AggregatesCache


@final
class QueryCube(ReprJsonable):
    r"""A cube of a :class:`~atoti.QuerySession`."""

    def __init__(
        self,
        identifier: CubeIdentifier,
        /,
        *,
        atoti_client: AtotiClient,
        java_api: JavaApi | None,
    ):
        self._atoti_client: Final = atoti_client
        self._identifier: Final = identifier
        self.__java_api: Final = java_api

    @property
    def _java_api(self) -> JavaApi:
        if self.__java_api is None:
            raise LiveExtensionUnavailableError
        return self.__java_api

    @property
    def name(self) -> str:
        return self._identifier.cube_name

    @property
    def data_cube_ids(self) -> AbstractSet[str]:
        assert self._atoti_client._graphql_client
        cluster = check_named_object_defined(
            self._atoti_client._graphql_client.get_cluster_members(
                self.name
            ).data_model.cube,
            "query cube",
            self.name,
        ).cluster
        return (
            frozenset()
            if cluster is None
            else frozenset(node.name for node in cluster.nodes)
        )

    @property
    def aggregates_cache(self) -> AggregatesCache:
        """Aggregates cache of the cube."""
        return AggregatesCache(
            cube_identifier=self._identifier,
            get_capacity=self._java_api.get_aggregates_cache_capacity,
            set_capacity=self._java_api.set_aggregates_cache_capacity,
        )

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {"name": self.name},
            {"expanded": False, "root": self.name},
        )
