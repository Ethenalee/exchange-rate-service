from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "exchange-rate-service"
    APP_ENV: str = "local"
    APP_COMPONENT: str = "server"
    SERVER_PORT: int = 5000
    DB_MAX_POOL_SIZE: int = 2
    DB_MIN_POOL_SIZE: int = 1
    DB_NAME: str = "exchange_rate_dev"
    DB_SSL: str = "prefer"
    CONNECTION_RETRIES: int = 5
    READ_DB_HOST: str = "postgres"
    READ_DB_PASS: str = "password"
    READ_DB_PORT: int = 5432
    READ_DB_USER: str = "postgres"
    WRITE_DB_HOST: str = "postgres"
    WRITE_DB_PASS: str = "password"
    WRITE_DB_PORT: int = 5432
    WRITE_DB_USER: str = "postgres"
    KAFKA_SERVER: str = "kafka:29092"
    REDIS_DSN: str = "redis://redis:6379"

    EXCHANGERATE_API_URL: str = "https://open.exchangerate-api.com"
    EXCHANGE_POLLING_TIME_IN_SECONDS: int = 86400
    EXCHANGE_RATES_TOPIC: str = f"exchange_rate_service_exchange_rates_{APP_ENV}"
    EXCHANGE_RATES_CONSUMER_GROUP_ID: str = f"exchange_rate_service_exchange_rates_processor_{APP_ENV}"
    EXCHANGE_RATES_CACHE_KEY: str = "exchangerate_api_timestamp"


settings = Settings(_env_file=".env")
