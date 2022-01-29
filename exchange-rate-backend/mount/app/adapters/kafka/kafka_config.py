from dataclasses import dataclass


@dataclass(frozen=True)
class KafkaConsumerConfig:
    bootstrap_servers: str
    consumer_group_id: str
    topic: str


@dataclass(frozen=True)
class KafkaProducerConfig:
    bootstrap_servers: str
