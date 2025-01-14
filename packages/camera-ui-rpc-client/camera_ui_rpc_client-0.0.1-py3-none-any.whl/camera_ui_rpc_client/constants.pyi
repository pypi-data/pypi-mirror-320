from .typings import ClientMetrics as ClientMetrics
from typing import Any, Final, Literal

class STATES:
    STARTING: Literal['starting']
    RUNNING: Literal['running']
    STOPPING: Literal['stopping']
    STOPPED: Literal['stopped']
    ERROR: Literal['error']

class SUBJECTS:
    class HEALTH:
        PING: Literal['health.ping']
        PONG: Literal['health.pong']
    class SERVER:
        STATUS: Literal['server.status']
        BROADCAST: Literal['server.broadcast']
    class PLUGIN:
        REGISTER: Literal['plugin.register']
        UNREGISTER: Literal['plugin.unregister']
        STATUS: Literal['plugin.status']
    class SERVICE:
        REGISTER: Literal['service.register']
        UNREGISTER: Literal['service.unregister']
        STATUS: Literal['service.status']
    class METRICS:
        UPDATE: Literal['metrics.update']

class MESSAGE:
    class TYPES:
        REQUEST: Literal['request']
        RESPONSE: Literal['response']
        BROADCAST: Literal['broadcast']
        RPC_REQUEST: Literal['rpcrequest']
        RPC_RESPONSE: Literal['rpcresponse']
        RPC_STREAM_REQUEST: Literal['rpcstreamrequest']
        DIRECT: Literal['direct']
    class PRIORITIES:
        HIGH: Literal['high']
        NORMAL: Literal['normal']
        LOW: Literal['low']
    class HEADERS:
        CORRELATION_ID: Literal['correlation-id']
        REQUEST_ID: Literal['request-id']
        TIMESTAMP: Literal['timestamp']
        PRIORITY: Literal['priority']
        TTL: Literal['ttl']

class DEFAULTS:
    class TIMEOUTS:
        CONNECTION: Final[int]
        REQUEST: Final[int]
        RPC: Final[int]
    class INTERVALS:
        HEARTBEAT: Final[int]
        CLEANUP: Final[int]
        METRICS: Final[int]
    class RETRY:
        MAX_RECONNECT_ATTEMPTS: Final[int]
        MIN_DELAY: Final[int]
        MAX_DELAY: Final[int]
    class METRICS:
        TTL: Final[int]

class VALIDATION:
    class LIMITS:
        MIN_ID_LENGTH: Final[int]
        MAX_ID_LENGTH: Final[int]
        MIN_NAME_LENGTH: Final[int]
        MAX_NAME_LENGTH: Final[int]
        MAX_DESC_LENGTH: Final[int]
        MAX_SIGNATURE_AGE: Final[int]

DEFAULT_CLIENT_METRICS: ClientMetrics
BASE_METRICS: dict[str, Any]
