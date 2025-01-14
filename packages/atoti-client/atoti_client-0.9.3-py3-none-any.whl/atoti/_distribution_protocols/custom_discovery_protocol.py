from typing import final

from pydantic.dataclasses import dataclass
from typing_extensions import override

from .._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from .discovery_protocol import DiscoveryProtocol


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class CustomDiscoveryProtocol(DiscoveryProtocol):
    protocol_name: str
    xml: str

    @property
    @override
    def _protocol_name(self) -> str:
        return self.protocol_name

    @property
    @override
    def _xml(self) -> str:
        return self.xml
