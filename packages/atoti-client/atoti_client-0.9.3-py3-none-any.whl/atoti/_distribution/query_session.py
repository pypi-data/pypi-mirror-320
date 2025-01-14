from __future__ import annotations

from collections.abc import MutableMapping
from contextlib import AbstractContextManager, ExitStack
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from atoti._basic_credentials import BasicCredentials
from atoti.security.security import Security

from .._atoti_client import AtotiClient
from .._java_api import JavaApi
from .._started_session_resources import started_session_resources
from ..config import SessionConfig
from .clusters import Clusters
from .query_cubes import QueryCubes

if TYPE_CHECKING:
    # pylint: disable=nested-import,undeclared-dependency
    from _atoti_server import ServerSubprocess


@final
class QuerySession(AbstractContextManager["QuerySession"]):
    @classmethod
    def start(
        cls,
        config: SessionConfig | None = None,
        /,
    ) -> QuerySession:
        if config is None:
            config = SessionConfig()

        with ExitStack() as exit_stack:
            atoti_client, java_api, server_subprocess, session_id = (
                exit_stack.enter_context(
                    started_session_resources(
                        address=None,
                        config=config,
                        enable_py4j_auth=True,
                        distributed=True,
                        py4j_server_port=None,
                        start_application=True,
                    ),
                )
            )
            assert server_subprocess is not None
            session = cls(
                atoti_client=atoti_client,
                java_api=java_api,
                server_subprocess=server_subprocess,
                session_id=session_id,
            )
            session._exit_stack.push(exit_stack.pop_all())
            return session

    def __init__(
        self,
        *,
        atoti_client: AtotiClient,
        java_api: JavaApi,
        server_subprocess: ServerSubprocess,
        session_id: str,
    ):
        self._atoti_client: Final = atoti_client
        self._exit_stack: Final = ExitStack()
        self._id: Final = session_id
        self._java_api: Final = java_api
        self._server_subprocess: Final = server_subprocess

    @override
    def __exit__(  # pylint: disable=too-many-positional-parameters
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        exception_traceback: TracebackType | None,
    ) -> None:
        self._exit_stack.__exit__(exception_type, exception_value, exception_traceback)

    def close(self) -> None:
        """Close this session and free all associated resources."""
        self.__exit__(None, None, None)

    def __del__(self) -> None:
        # Use private method to avoid sending a telemetry event that would raise `RuntimeError: cannot schedule new futures after shutdown` when calling `ThreadPoolExecutor.submit()`.
        self.__exit__(None, None, None)

    @property
    def logs_path(self) -> Path:
        return self._server_subprocess.logs_path

    @property
    def url(self) -> str:
        return self._atoti_client.activeviam_client.url

    @property
    def cubes(self) -> QueryCubes:
        return QueryCubes(atoti_client=self._atoti_client, java_api=self._java_api)

    @property
    def _basic_credentials(self) -> MutableMapping[str, str] | None:
        return BasicCredentials(java_api=self._java_api)

    @property
    def security(self) -> Security:
        return Security(
            activeviam_client=self._atoti_client.activeviam_client,
            basic_credentials=self._basic_credentials,
            is_query_session=True,
        )

    @property
    def clusters(self) -> Clusters:
        return Clusters(
            # A query session does not perform auto-join
            trigger_auto_join=lambda: False,
            java_api=self._java_api,
        )
