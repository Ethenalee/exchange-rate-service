import prometheus_client

from app.commons import logger
from ..writer import handler, WriterOutput


class LogWriter(WriterOutput):
    @handler("cache", "init")
    def log_cache_init(self):
        logger.info("CACHE: Init connection")

    @handler("exchange_rates_processor", "processor", "start")
    def log_processor_start(self):
        logger.info("EXCHANGE RATES PROCESSOR: START")

    @handler("exchange_rates_processor", "processor", "end")
    def log_processor_end(self, timestamp: str):
        logger.info(f"EXCHANGE RATES PROCESSOR: {timestamp} END")


class MetricsWriter(WriterOutput):
    NAMESPACE = "exchange_rates_processor"

    def __init__(self):
        self.processor_processed_metrics = {}
        super().__init__()

    @handler("exchange_rates_processor", "processor", "end")
    def count_processor_end(self, timestamp: str):
        metrics_key = timestamp

        if metrics_key not in self.processor_processed_metrics:
            self.processor_processed_metrics[metrics_key] = {
                "counter": prometheus_client.Counter(
                    f"{self.NAMESPACE}_{timestamp}_processor_count",
                    "Number of exchange rate processed",
                ),
            }
        self.processor_processed_metrics[metrics_key]["counter"].inc()
