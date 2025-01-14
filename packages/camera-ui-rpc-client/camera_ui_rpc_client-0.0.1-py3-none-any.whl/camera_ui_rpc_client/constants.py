from datetime import datetime
from typing import Any, Final, Literal

from .typings import ClientMetrics


class STATES:
    STARTING: Literal["starting"] = "starting"
    RUNNING: Literal["running"] = "running"
    STOPPING: Literal["stopping"] = "stopping"
    STOPPED: Literal["stopped"] = "stopped"
    ERROR: Literal["error"] = "error"


class SUBJECTS:
    class HEALTH:
        PING: Literal["health.ping"] = "health.ping"
        PONG: Literal["health.pong"] = "health.pong"

    class SERVER:
        STATUS: Literal["server.status"] = "server.status"
        BROADCAST: Literal["server.broadcast"] = "server.broadcast"

    class PLUGIN:
        REGISTER: Literal["plugin.register"] = "plugin.register"
        UNREGISTER: Literal["plugin.unregister"] = "plugin.unregister"
        STATUS: Literal["plugin.status"] = "plugin.status"

    class SERVICE:
        REGISTER: Literal["service.register"] = "service.register"
        UNREGISTER: Literal["service.unregister"] = "service.unregister"
        STATUS: Literal["service.status"] = "service.status"

    class METRICS:
        UPDATE: Literal["metrics.update"] = "metrics.update"


class MESSAGE:
    class TYPES:
        REQUEST: Literal["request"] = "request"
        RESPONSE: Literal["response"] = "response"
        BROADCAST: Literal["broadcast"] = "broadcast"
        RPC_REQUEST: Literal["rpcrequest"] = "rpcrequest"
        RPC_RESPONSE: Literal["rpcresponse"] = "rpcresponse"
        RPC_STREAM_REQUEST: Literal["rpcstreamrequest"] = "rpcstreamrequest"
        DIRECT: Literal["direct"] = "direct"

    class PRIORITIES:
        HIGH: Literal["high"] = "high"
        NORMAL: Literal["normal"] = "normal"
        LOW: Literal["low"] = "low"

    class HEADERS:
        CORRELATION_ID: Literal["correlation-id"] = "correlation-id"
        REQUEST_ID: Literal["request-id"] = "request-id"
        TIMESTAMP: Literal["timestamp"] = "timestamp"
        PRIORITY: Literal["priority"] = "priority"
        TTL: Literal["ttl"] = "ttl"


class DEFAULTS:
    class TIMEOUTS:
        CONNECTION: Final[int] = 5000  # 5 seconds
        REQUEST: Final[int] = 5000  # 5 seconds
        RPC: Final[int] = 5000  # 5 seconds

    class INTERVALS:
        HEARTBEAT: Final[int] = 3000  # 3 seconds
        CLEANUP: Final[int] = 60000  # 1 minute
        METRICS: Final[int] = 5000  # 5 seconds

    class RETRY:
        MAX_RECONNECT_ATTEMPTS: Final[int] = -1
        MIN_DELAY: Final[int] = 1000  # 1 second
        MAX_DELAY: Final[int] = 5000  # 5 seconds

    class METRICS:
        TTL: Final[int] = 60000  # 1 minute


class VALIDATION:
    class LIMITS:
        MIN_ID_LENGTH: Final[int] = 3
        MAX_ID_LENGTH: Final[int] = 64
        MIN_NAME_LENGTH: Final[int] = 1
        MAX_NAME_LENGTH: Final[int] = 128
        MAX_DESC_LENGTH: Final[int] = 500
        MAX_SIGNATURE_AGE: Final[int] = 300000  # 5 minutes


DEFAULT_CLIENT_METRICS: ClientMetrics = {
    "timestamp": int(datetime.now().timestamp() * 1000),
    "startTime": int(datetime.now().timestamp() * 1000),
    "requests": {"total": 0, "active": 0, "errors": 0, "perSecond": 0, "avgResponseTime": 0},
    "messages": {"published": 0, "received": 0, "errors": 0},
    "rpc": {"total": 0, "active": 0, "errors": 0},
    "subscriptions": {"active": 0, "messageHandlers": 0, "requestHandlers": 0, "rpcHandlers": 0},
}

BASE_METRICS: dict[str, Any] = {
    "requests": {
        "total": 0,
        "active": 0,
        "errors": 0,
        "timings": {},
        "in_window": {
            "count": 0,
            "errors": 0,
            "response_times": [],
            "start_time": int(datetime.now().timestamp() * 1000),
        },
    },
    "messages": {"published": 0, "received": 0, "errors": 0},
    "rpc": {"total": 0, "active": 0, "errors": 0},
    "subscriptions": {"active": 0, "message_handlers": 0, "request_handlers": 0, "rpc_handlers": 0},
}
