import asyncio
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from datetime import datetime
from typing import Any, Callable, TypeVar, Union

from .base.client import RPCClient
from .base.connection import RPCConnectionManager
from .base.errors import ERROR_CODES, ErrorFactory
from .base.messaging import BaseMessaging
from .base.rpc import RPCConnection
from .constants import DEFAULTS, STATES, SUBJECTS
from .typings import (
    ClientConnectionOptions,
    ClientMetrics,
    ClientStatus,
    ConnectionMessage,
    ConnectionState,
    Message,
    ResponseMessage,
    RPCOptions,
)
from .utils.logger import setup_logger
from .utils.subscriptions import SubscriptionWrapper
from .utils.tasks import TaskSet
from .utils.validate import ValidationUtils

logger = setup_logger("camera:ui:client:instance")

# Types
T = TypeVar("T")
R = TypeVar("R")


class ClientInstance(BaseMessaging, ABC):
    def __init__(
        self,
        options: ClientConnectionOptions,
    ):
        super().__init__()
        self.options = options

        ValidationUtils.validate_connection_options(options)

        self._client = RPCClient("plugin", options)
        self._status: ConnectionState = STATES.STOPPED
        self._error: Exception | None = None
        self._metrics_task: asyncio.Task[Any] | None = None
        self._task_set = TaskSet("ClientInstance")

    async def start(self) -> None:
        try:
            if self._status == STATES.RUNNING:
                return

            # Call client-specific before start hook
            if hasattr(self, "on_before_start"):
                await self.on_before_start()

            # Connect to NATS
            await self._client.connect()

            # Setup subscriptions
            await self._setup_subscriptions()

            # Start metrics collection
            self._start_metrics_collection()

            # Update state
            await self._update_status(STATES.RUNNING)
            logger.debug(f"Client {self.options['metadata']['id']} started successfully")

            # Call client-specific start logic
            asyncio.create_task(self.on_start())

            # Call client-specific after start hook
            if hasattr(self, "on_after_start"):
                self.on_after_start()

        except Exception as e:
            raise ErrorFactory.connection.connection_failed(
                e,
                {
                    "description": "Failed to start client",
                    "code": ERROR_CODES.CONNECTION.FAILED,
                    "metadata": {
                        "type": "plugin",
                        "metadata": self.options["metadata"],
                    },
                },
            ) from e

    async def stop(self) -> None:
        try:
            if self._status == STATES.STOPPED:
                return

            # Update state
            await self._update_status(STATES.STOPPING)

            # Call client-specific before stop hook
            if hasattr(self, "on_before_stop"):
                await self.on_before_stop()

            # Stop metrics collection
            self._stop_metrics_collection()

            # Update state
            await self._update_status(STATES.STOPPED)

            # Disconnect from NATS
            await self._client.disconnect()

            # Call client-specific stop logic
            await self.on_stop()

            # Call client-specific after stop hook
            if hasattr(self, "on_after_stop"):
                self.on_after_stop()

            logger.debug(f"Client {self.options['metadata']['name']} stopped successfully")

        except Exception as e:
            raise ErrorFactory.connection.connection_failed(
                e,
                {
                    "description": "Failed to stop client",
                    "code": ERROR_CODES.CONNECTION.FAILED,
                    "metadata": {
                        "type": "plugin",
                        "metadata": self.options["metadata"],
                    },
                },
            ) from e

    async def send_to_plugin(self, plugin_id: str, data: Any) -> None:
        return await self._client.send_to_plugin(plugin_id, data)

    async def send_to_service(self, service_id: str, data: Any) -> None:
        return await self._client.send_to_service(service_id, data)

    async def send_to_server(self, data: Any) -> None:
        return await self._client.send_to_server(data)

    async def request_from_plugin(
        self, plugin_id: str, data: Any, timeout: int | None = None
    ) -> ResponseMessage[Any]:
        return await self._client.request_from_plugin(plugin_id, data, timeout)

    async def request_from_service(
        self, service_id: str, data: Any, timeout: int | None = None
    ) -> ResponseMessage[Any]:
        return await self._client.request_from_service(service_id, data, timeout)

    async def request_from_server(self, data: Any, timeout: int | None = None) -> ResponseMessage[Any]:
        return await self._client.request_from_server(data, timeout)

    async def on_plugin_message(
        self, plugin_id: str | None, handler: Callable[[T], Union[R, Awaitable[R | None]]]
    ) -> None:
        await self._client.on_plugin_message(plugin_id, handler)

    async def on_service_message(
        self, service_id: str | None, handler: Callable[[T], Union[R, Awaitable[R | None]]]
    ) -> None:
        await self._client.on_service_message(service_id, handler)

    async def on_server_message(
        self, handler: Callable[[T], Union[R, Awaitable[R | None]]]
    ) -> SubscriptionWrapper:
        return await self._client.on_server_message(handler)

    async def register_rpc_handler(
        self, namespace: str, handler: Union[dict[str, Callable[..., Any]], object]
    ) -> None:
        await self._client.register_rpc_handler(namespace, handler)

    async def unregister_rpc_handler(self, namespace: str) -> None:
        await self._client.unregister_rpc_handler(namespace)

    async def create_rpc_proxy(
        self, type: type[T], namespace: str, rpc_options: RPCOptions | None = None
    ) -> T:
        return await self._client.create_rpc_proxy(type, namespace, rpc_options)

    async def create_rpc_connection(
        self, namespace: str, rpc_options: RPCOptions | None = None
    ) -> RPCConnection:
        return await self._client.create_rpc_connection(namespace, rpc_options)

    async def disconnect_rpc_connection(self, namespace: str) -> None:
        return await self._client.disconnect_rpc_connection(namespace)

    def get_status(self) -> ClientStatus:
        return {
            "id": self.options["metadata"]["id"],
            "type": "plugin",
            "state": self._status,
            "error": self._error,
            "metadata": self.options["metadata"],
        }

    def is_connected(self) -> bool:
        return self._client.is_connected()

    def get_connection_manager(self) -> RPCConnectionManager:
        return self._client.get_connection_manager()

    def get_connection_anager(self) -> RPCConnectionManager:
        return self._client.get_connection_manager()

    def is_running(self) -> bool:
        return self._status == STATES.RUNNING

    def is_server_running(self) -> bool:
        return self._client.is_server_running()

    # Abstract methods that clients must implement
    @abstractmethod
    async def on_start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_stop(self) -> None:
        raise NotImplementedError

    # Optional lifecycle hooks
    async def on_before_start(self) -> None:
        pass

    def on_after_start(self) -> None:
        pass

    async def on_before_stop(self) -> None:
        pass

    def on_after_stop(self) -> None:
        pass

    async def _setup_subscriptions(self) -> None:
        await self.subscribe(
            f"{SUBJECTS.HEALTH.PING}.plugin.{self.options['metadata']['id']}", self._handle_ping
        )

    def _start_metrics_collection(self) -> None:
        self._stop_metrics_collection()
        self._metrics_task = self._task_set.add(self._metrics_collection_loop())

    def _stop_metrics_collection(self) -> None:
        self._task_set.remove(self._metrics_task)

    async def _metrics_collection_loop(self) -> None:
        """Continuous loop for collecting and publishing metrics."""
        while True:
            try:
                metrics = self._aggregate_metrics()
                subject = f"{SUBJECTS.METRICS.UPDATE}.plugin.{self.options['metadata']['id']}"
                await self.publish(subject, metrics)
                logger.debug(f"Published metrics for {self.options['metadata']['id']}: {metrics}")
            except Exception as e:
                logger.debug(f"Failed to publish metrics for {self.options['metadata']['id']}: {e}")

            await asyncio.sleep(DEFAULTS.INTERVALS.METRICS / 1000)  # Convert ms to seconds

    def _aggregate_metrics(self) -> ClientMetrics:
        """Aggregate metrics from all connection managers."""
        connection_managers = self._client.get_connection_managers()
        logger.debug(f"Aggregating metrics from connection managers: {len(connection_managers)}")

        # Initialize aggregated metrics
        aggregated: ClientMetrics = {
            "timestamp": int(datetime.now().timestamp() * 1000),  # Current time in milliseconds
            "startTime": min(cm.get_metrics()["startTime"] for cm in connection_managers),
            "requests": {"total": 0, "active": 0, "errors": 0, "perSecond": 0, "avgResponseTime": 0},
            "messages": {"published": 0, "received": 0, "errors": 0},
            "rpc": {"total": 0, "active": 0, "errors": 0},
            "subscriptions": {"active": 0, "messageHandlers": 0, "requestHandlers": 0, "rpcHandlers": 0},
        }

        total_requests: int = 0
        total_response_time: float = 0

        # Collect metrics from all managers
        for manager in connection_managers:
            metrics = manager.get_metrics()

            # Accumulate counters
            aggregated["requests"]["total"] += metrics["requests"]["total"]
            aggregated["requests"]["active"] += metrics["requests"]["active"]
            aggregated["requests"]["errors"] += metrics["requests"]["errors"]

            # Collect data for weighted average of RPS and response time
            request_weight = metrics["requests"]["total"]
            if request_weight > 0:
                total_requests += request_weight
                total_response_time += metrics["requests"]["avgResponseTime"] * request_weight
                aggregated["requests"]["perSecond"] += metrics["requests"]["perSecond"]

            # Accumulate other metrics
            aggregated["messages"]["published"] += metrics["messages"]["published"]
            aggregated["messages"]["received"] += metrics["messages"]["received"]
            aggregated["messages"]["errors"] += metrics["messages"]["errors"]

            aggregated["rpc"]["total"] += metrics["rpc"]["total"]
            aggregated["rpc"]["active"] += metrics["rpc"]["active"]
            aggregated["rpc"]["errors"] += metrics["rpc"]["errors"]

            # For subscriptions we take the current values
            aggregated["subscriptions"]["active"] += metrics["subscriptions"]["active"]
            aggregated["subscriptions"]["messageHandlers"] += metrics["subscriptions"]["messageHandlers"]
            aggregated["subscriptions"]["requestHandlers"] += metrics["subscriptions"]["requestHandlers"]
            aggregated["subscriptions"]["rpcHandlers"] += metrics["subscriptions"]["rpcHandlers"]

        # Calculate final values
        if total_requests > 0:
            aggregated["requests"]["avgResponseTime"] = total_response_time / total_requests

        # RPS is averaged across all managers
        if connection_managers:
            aggregated["requests"]["perSecond"] = aggregated["requests"]["perSecond"] / len(
                connection_managers
            )

        return aggregated

    async def _handle_ping(self, _: Message[ConnectionMessage]) -> None:
        await self._client.publish(
            f"{SUBJECTS.PLUGIN.STATUS}.{self.options['metadata']['id']}", self.get_status()["state"]
        )

    async def _update_status(self, state: ConnectionState, error: Exception | None = None) -> None:
        if self._status == state:
            return

        self._status = state
        self._error = error
        logger.debug(f"Client {self.options['metadata']['name']} state changed to {state}")

        try:
            if self._client.is_connected():
                await self._client.publish(
                    f"{SUBJECTS.PLUGIN.STATUS}.{self.options['metadata']['id']}", self.get_status()["state"]
                )
            else:
                logger.debug("Skipping status update: Not connected to server")

        except Exception as e:
            nats_error = ErrorFactory.client.internal_error(
                e,
                {
                    "description": "Failed to update state",
                    "code": ERROR_CODES.CLIENT.INTERNAL_ERROR,
                    "metadata": {
                        "type": "plugin",
                        "metadata": self.options["metadata"],
                    },
                },
            )
            logger.debug(f"Failed to update state: {nats_error}")
