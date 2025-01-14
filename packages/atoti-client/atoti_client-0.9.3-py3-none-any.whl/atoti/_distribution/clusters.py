from collections.abc import Callable, Mapping, Set as AbstractSet
from typing import Final, final

from typing_extensions import override

from .._collections import DelegatingMutableMapping
from .._identification import ClusterName
from .._java_api import JavaApi
from ..config._cluster_config import ClusterConfig


@final
class Clusters(DelegatingMutableMapping[ClusterName, ClusterConfig]):
    def __init__(self, *, trigger_auto_join: Callable[[], bool], java_api: JavaApi):
        self._trigger_auto_join: Final = trigger_auto_join
        self._java_api: Final = java_api

    @override
    def _get_delegate(
        self, *, key: ClusterName | None
    ) -> Mapping[ClusterName, ClusterConfig]:
        if key is None:
            return self._java_api.get_distributed_clusters()
        cluster = self._java_api.get_distributed_cluster(key)
        return {} if cluster is None else {key: cluster}

    @override
    def _update_delegate(self, other: Mapping[ClusterName, ClusterConfig]) -> None:
        for cluster_name, cluster_config in other.items():
            self._java_api.create_distributed_cluster(
                cluster_name=cluster_name,
                cluster_config=cluster_config,
            )

        self._java_api.refresh()
        if self._trigger_auto_join():
            self._java_api.auto_join_new_distributed_clusters(
                cluster_names=other.keys()
            )
            self._java_api.refresh()

    @override
    def _delete_delegate_keys(self, keys: AbstractSet[ClusterName]) -> None:
        for key in keys:
            self._java_api.delete_distributed_cluster(key)

        self._java_api.refresh()
