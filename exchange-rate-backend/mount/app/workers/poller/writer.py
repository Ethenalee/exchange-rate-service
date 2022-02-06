import prometheus_client

from app.commons import logger
from ..writer import handler, WriterOutput


class LogWriter(WriterOutput):
    @handler("cache", "init")
    def log_cache_init(self):
        logger.info("CACHE: Init connection")

    @handler("exchange_rates_poll", "poller", "start")
    def log_poller_start(self):
        logger.info("EXCHANGE RATES POLLER: START")

    @handler("exchange_rates_poll", "poller", "end")
    def log_poller_end(self, timestamp: str):
        logger.info(f"EXCHANGE RATES POLLER: {timestamp} END")

    @handler("exchange_rates_poll", "poller", "pass")
    def log_poller_pass(self):
        logger.info("EXCHANGE RATES POLLER: ALREADY POLLED")


class MetricsWriter(WriterOutput):
    NAMESPACE = "exchange_rates_poller"

    def __init__(self):
        self.processor_processed_metrics = {}
        super().__init__()

    @handler("exchange_rates_poll", "poller", "end")
    def count_poller_end(self, timestamp: str):
        metrics_key = timestamp

        if metrics_key not in self.processor_processed_metrics:
            self.processor_processed_metrics[metrics_key] = {
                "counter": prometheus_client.Counter(
                    f"{self.NAMESPACE}_{timestamp}_poll_count",
                    "Number of exchange rate polls",
                ),
            }
        self.processor_processed_metrics[metrics_key]["counter"].inc()
