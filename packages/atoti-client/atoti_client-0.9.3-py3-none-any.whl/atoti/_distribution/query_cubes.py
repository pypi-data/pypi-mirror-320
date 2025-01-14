from collections.abc import Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._atoti_client import AtotiClient
from .._collections import DelegatingConvertingMapping
from .._identification import CubeIdentifier, CubeName
from .._ipython import ReprJson, ReprJsonable
from .._java_api import JavaApi
from .query_cube import QueryCube
from .query_cube_config import QueryCubeConfig


@final
class QueryCubes(
    DelegatingConvertingMapping[CubeName, CubeName, QueryCube, QueryCubeConfig],
    ReprJsonable,
):
    r"""Manage the :class:`~atoti.QueryCube`\ s of a :class:`~atoti.QuerySession`."""

    def __init__(
        self,
        *,
        atoti_client: AtotiClient,
        java_api: JavaApi,
    ):
        self._atoti_client: Final = atoti_client
        self._java_api: Final = java_api

    def _get_cube_identifiers(self, *, key: CubeName | None) -> list[CubeIdentifier]:
        assert self._atoti_client._graphql_client

        if key is None:
            return [
                CubeIdentifier(cube_name=cube.name)
                for cube in self._atoti_client._graphql_client.get_cubes().data_model.cubes
            ]

        cube = self._atoti_client._graphql_client.find_cube(
            cube_name=key,
        ).data_model.cube
        return [CubeIdentifier(cube_name=cube.name)] if cube else []

    @override
    def _get_delegate(self, *, key: CubeName | None) -> Mapping[CubeName, QueryCube]:
        return {
            identifier.cube_name: QueryCube(
                identifier,
                atoti_client=self._atoti_client,
                java_api=self._java_api,
            )
            for identifier in self._get_cube_identifiers(key=key)
        }

    @override
    def _update_delegate(
        self,
        other: Mapping[CubeName, QueryCubeConfig],
        /,
    ) -> None:
        for cube_name, cube_definition in other.items():
            self._java_api.create_query_cube(
                cube_name,
                cluster_name=cube_definition.cluster,
                distribution_levels=cube_definition.distribution_levels,
                catalog_names=cube_definition.catalog_names,
                application_names=cube_definition.application_names,
            )
        self._java_api.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[CubeName], /) -> None: ...

    @override
    def _repr_json_(self) -> ReprJson:
        return (
            {name: cube._repr_json_()[0] for name, cube in sorted(self.items())},
            {"expanded": False, "root": "Cubes"},
        )
