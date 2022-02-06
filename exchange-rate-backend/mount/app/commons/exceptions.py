from enum import Enum


class AppErrorCode(str, Enum):
    INVALID_PARAMS = "INVALID_PARAMS"
    RATES_NOT_AVAILABLE = "RATES_NOT_AVAILABLE"
    PROVIDER_NOT_AVAILALBE = "PROVIDER_NOT_AVAILALBE"

    # Health Checkxx
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    KAFKA_CONSUMER_DISCONNECTED = "KAFKA_CONSUMER_DISCONNECTED"
    KAFKA_PRODUCER_DISCONNECTED = "KAFKA_PRODUCER_DISCONNECTED"
    CACHE_DISCONNECTED = "CACHE_DISCONNECTED"


class AppErrorMessage(str, Enum):
    INVALID_PARAMS = "invalid params"
    RATES_NOT_AVAILABLE = "rates not available"
    PROVIDER_NOT_AVAILALBE = "provider not available"

    # Health Checkxx
    DATABASE_UNAVAILABLE = "database_unavailable"
    KAFKA_CONSUMER_DISCONNECTED = "kafka_consumer_disconnected"
    KAFKA_PRODUCER_DISCONNECTED = "kafka_producer_disconnected"
    CACHE_DISCONNECTED = "cache_disconnected"


class AppError(Exception):
    def __init__(self, code: AppErrorCode, message: str = ""):
        self.code = code.value
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{repr(super())} code={self.code} message={self.message}>"


class InvalidParamError(AppError):
    def __init__(self, code: AppErrorCode, message: str = ""):
        super().__init__(code, message)
