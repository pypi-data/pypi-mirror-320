from collections.abc import Set as AbstractSet
from typing import Annotated, final

from pydantic import Field, field_serializer
from pydantic.dataclasses import dataclass

from atoti._distribution_protocols.discovery_protocol import DiscoveryProtocol

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
# Do not make this class public before solving these issues:
# - `cube_port` makes no sense next to an attribute named `cube_url` as URLs must contain ports when they're not using the protocol's default one.
class ClusterConfig:
    allowed_application_names: AbstractSet[str]
    cube_url: str | None = None
    cube_port: int | None = None
    discovery_protocol: Annotated[
        DiscoveryProtocol | None,
        Field(serialization_alias="discovery_protocol_xml"),
    ] = None
    auth_token: str

    @field_serializer("discovery_protocol")
    def _serialize_discovery_protocol(
        self, value: DiscoveryProtocol | None
    ) -> str | None:
        return None if value is None else value._xml
