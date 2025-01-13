"""
This is a scrapy extension that pushes metrics to a Prometheus Pushgateway.
"""

from prometheus_client import Gauge, CollectorRegistry, push_to_gateway
from scrapy.exceptions import NotConfigured
from scrapy import signals
from scrapy.crawler import Crawler


class ScrapyPrometheusExtension:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        if not crawler.settings.getbool("PROMETHEUS_ENABLED", True):
            raise NotConfigured
        self.gateway = crawler.settings.get("PROMETHEUS_GATEWAY")
        if self.gateway is None:
            raise NotConfigured("PROMETHEUS_GATEWAY is missing")
        
        self.registry = CollectorRegistry()

        self.spr_item_scraped = Gauge("spr_item_scraped", "...", labelnames=["spider"], registry=self.registry)
        self.spr_item_dropped = Gauge("spr_item_dropped", "...", labelnames=["spider"], registry=self.registry)
        self.spr_request_count = Gauge("spr_request_count", "...", labelnames=["spider", "method"], registry=self.registry)
        self.spr_response_count = Gauge("spr_response_count", "Number of responses received by spider (callback)", labelnames=["spider"], registry=self.registry)
        self.spr_response_status_count = Gauge("spr_response_status_count", "...", labelnames=["spider", "status"], registry=self.registry)
        self.spr_duplicate_filtered = Gauge("spr_duplicate_filtered", "...", labelnames=["spider"], registry=self.registry)
        self.spr_memusage_max = Gauge("spr_memusage_max", "...", labelnames=["spider"], registry=self.registry)
        self.spr_request_depth = Gauge("spr_request_depth", "...", labelnames=["spider"], registry=self.registry)
        self.spr_offsite_domains = Gauge("spr_offsite_domains", "...", labelnames=["spider"], registry=self.registry)
        self.spr_offsite_filtered = Gauge("spr_offsite_filtered", "...", labelnames=["spider"], registry=self.registry)
        self.spr_elapsed_time = Gauge("spr_elapsed_time", "...", labelnames=["spider"], registry=self.registry)

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        ext = cls(crawler)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def update_spr_metrics(self, spider):
        self.spr_item_scraped.labels(spider.name).set(self.crawler.stats.get_value("item_scraped_count", 0))
        self.spr_item_dropped.labels(spider.name).set(self.crawler.stats.get_value("item_dropped_count", 0))

        for method in ["GET","POST"]:
            self.spr_request_count.labels(spider.name, method).set(self.crawler.stats.get_value(f"downloader/request_method_count/{method}", 0))
        self.spr_response_count.labels(spider.name).set(self.crawler.stats.get_value("response_received_count", 0))

        status_counts = {k.split('/')[-1]: v for k, v in self.crawler.stats.get_stats().items() if k.startswith('downloader/response_status_count/')}
        for status, count in status_counts.items():
            self.spr_response_status_count.labels(spider.name, status).set(count)

        self.spr_duplicate_filtered.labels(spider.name).set(self.crawler.stats.get_value("dupefilter/filtered", 0))
        self.spr_memusage_max.labels(spider.name).set(self.crawler.stats.get_value("memusage/max", 0))
        self.spr_request_depth.labels(spider.name).set(self.crawler.stats.get_value("request_depth_max", 0))
        self.spr_offsite_domains.labels(spider.name).set(self.crawler.stats.get_value("offsite/domains", 0))
        self.spr_offsite_filtered.labels(spider.name).set(self.crawler.stats.get_value("offsite/filtered", 0))
        self.spr_elapsed_time.labels(spider.name).set(self.crawler.stats.get_value("elapsed_time_seconds", 0))

    def spider_closed(self, spider, reason):
        self.update_spr_metrics(spider)
        push_to_gateway(self.gateway, job="scrapy", registry=self.registry)
        spider.logger.info("Metrics pushed to Prometheus")
