from .base.errors import SerializedError as SerializedError
from _typeshed import Incomplete
from typing import Any, Generic, Literal, Protocol, TypeVar
from typing_extensions import NotRequired, TypedDict

T = TypeVar('T')
R = TypeVar('R')
ConnectionState: Incomplete
MessageType: Incomplete

class Metadata(TypedDict):
    id: str
    name: str

class AuthConfig(TypedDict):
    user: str
    password: str

class ReconnectOptions(TypedDict, total=False):
    max_attempts: int
    min_delay: float
    max_delay: float

class TimeoutOptions(TypedDict, total=False):
    connect: float

class ClientConnectionOptions(TypedDict):
    endpoints: list[str]
    auth: AuthConfig
    metadata: Metadata
    reconnect: NotRequired[ReconnectOptions | None]
    timeout: NotRequired[TimeoutOptions | None]

class RoutingSource(TypedDict):
    id: str
    type: Literal['plugin', 'service', 'server']

class RoutingTarget(TypedDict):
    id: str
    type: Literal['plugin', 'service', 'server']

class RoutingMetadata(TypedDict):
    source: RoutingSource
    target: RoutingTarget | None

class Message(TypedDict, Generic[T]):
    type: MessageType
    data: T
    id: str
    timestamp: float
    metadata: Metadata
    routing: NotRequired[RoutingMetadata | None]

class RequestMessage(Message[T]):
    type: Literal['request']  # type: ignore
    subject: str
    replyTo: NotRequired[str | None]

class ResponseMessage(Message[R]):
    type: Literal['response']  # type: ignore
    requestId: str
    error: NotRequired[SerializedError | None]

class BroadcastMessage(Message[T]):
    type: Literal['broadcast']  # type: ignore
    error: NotRequired[SerializedError | None]

class RPCRequest(Message[T]):
    type: Literal['rpcrequest'] | Literal['rpcstreamrequest']  # type: ignore
    subject: str
    streamId: NotRequired[str | None]

class RPCResponse(Message[R]):
    type: Literal['rpcresponse']  # type: ignore
    requestId: str
    streamId: NotRequired[str | None]
    done: NotRequired[bool | None]
    error: NotRequired[SerializedError | None]

class GeneratorControl(TypedDict):
    type: Literal['return', 'throw']
    value: NotRequired[Any]

class GeneratorMessage(TypedDict):
    streamId: str
    args: NotRequired[tuple[Any, ...]]

class GeneratorResult(TypedDict):
    requestId: str
    streamId: NotRequired[str | None]
    value: NotRequired[Any]
    done: bool

class ConnectionMessage(TypedDict):
    sourceId: str
    sourceType: Literal['plugin', 'service']
    timestamp: float

class ClientMessage(TypedDict):
    clientId: str

class RegistrationResponse(TypedDict):
    success: bool
    serverMetadata: Metadata

class RPCHandler(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

class Disposable(Protocol):
    async def dispose(self) -> None: ...

class ClientStatus(TypedDict):
    id: str
    type: str
    state: ConnectionState
    error: Exception | None
    metadata: Metadata | None

class RPCOptions(TypedDict):
    timeout: int | None

class ClientRequestsMetrics(TypedDict):
    total: int
    active: int
    errors: int
    perSecond: float
    avgResponseTime: float

class ClientMessagesMetrics(TypedDict):
    published: int
    received: int
    errors: int

class ClientRPCMetrics(TypedDict):
    total: int
    active: int
    errors: int

class ClientSubscriptionsMetrics(TypedDict):
    active: int
    messageHandlers: int
    requestHandlers: int
    rpcHandlers: int

class ClientMetrics(TypedDict):
    timestamp: int
    startTime: int
    requests: ClientRequestsMetrics
    messages: ClientMessagesMetrics
    rpc: ClientRPCMetrics
    subscriptions: ClientSubscriptionsMetrics
