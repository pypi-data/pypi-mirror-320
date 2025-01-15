from datetime import datetime, timedelta, timezone
import time

import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from the_conf import TheConf

conf = TheConf(
    {
        "source_order": ["env", "files"],
        "config_files": [
            "/etc/updownio-exporter/updownio-exporter.json",
            "~/.config/updownio-exporter.json",
        ],
        "parameters": [
            {"name": {"default": "updownio-exporter"}},
            {"type": "list", "apikeys": {"type": str}},
            {"loop": [{"interval": {"default": 240}}]},
            {
                "prometheus": [
                    {"port": {"type": "int", "default": 9100}},
                    {"namespace": {"default": "updownio"}},
                ]
            },
        ],
    }
)


URL = "https://updown.io/api/%s?api-key=%s"
RESPONSE_TIME_BUCKETS = [125, 250, 500, 1000, 2000, 4000]
RATIO = 0.75
DAEMON = Gauge("daemon", "", ["name", "section", "status"])
APDEX = Gauge(
    "apdex",
    "apdex",
    ["alias"],
    namespace=conf.prometheus.namespace,
)
TIMINGS = Gauge(
    "timings",
    "timings",
    ["alias", "step"],
    namespace=conf.prometheus.namespace,
)
REQUEST_COUNT = Counter(
    "request",
    "request",
    ["alias", "tag"],
    namespace=conf.prometheus.namespace,
)
RESPONSE_TIME = Histogram(
    "response_time",
    "Response time",
    ["alias"],
    buckets=RESPONSE_TIME_BUCKETS,
    namespace=conf.prometheus.namespace,
)


def browse_request_by_response_time(metrics: dict, histogram: Histogram):
    seen = 0
    for bucket in RESPONSE_TIME_BUCKETS:
        count = metrics["requests"]["by_response_time"][f"under{bucket}"]
        for _ in range(count - seen):
            histogram.observe(bucket * RATIO)
        seen = count
    if metrics["requests"]["samples"] - seen > 0:
        for _ in range(metrics["requests"]["samples"] - seen):
            histogram.observe(RESPONSE_TIME_BUCKETS[-1] * 2)


def collect(api_key):
    response = requests.get(URL % ("checks", api_key), timeout=60)
    response.raise_for_status()
    checks = response.json()

    utcnow = datetime.now(tz=timezone.utc)
    utcmidnight = datetime(
        utcnow.year, utcnow.month, utcnow.day, tzinfo=timezone.utc
    )
    one_day = timedelta(days=1)
    for check in checks:
        alias = check["alias"].lower().replace(" ", "-")
        uri = f"checks/{check['token']}/metrics"
        url = URL % (uri, api_key)
        # increasing period for low sample check
        # period to two days on every even day
        if check["period"] > 1000 and not utcmidnight.day % 2:
            from_ = utcmidnight - one_day
        else:
            from_ = utcmidnight
        url += f"&from={from_.isoformat()}"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        metrics = response.json()
        if "apdex" in metrics:  # accounting apdex
            APDEX.labels(alias=alias).set(metrics["apdex"])
        # filling histogram
        histogram = RESPONSE_TIME.labels(alias)
        setattr(histogram, "_created", from_.timestamp())
        if "requests" in metrics:
            browse_request_by_response_time(metrics, histogram)
        # counting request
        for key, value in metrics.get("requests", {}).items():
            if isinstance(value, int):
                labeled_req_count = REQUEST_COUNT.labels(alias, key)
                setattr(labeled_req_count, "_created", from_.timestamp())
                labeled_req_count.inc(value)
        for step, timing in metrics.get("timings", {}).items():
            TIMINGS.labels(alias=alias, step=step).set(timing)


def main():
    labels = {"name": conf.name, "section": "config"}
    DAEMON.labels(status="loop-period", **labels).set(conf.loop.interval)
    DAEMON.labels(status="item-count", **labels).set(len(conf.apikeys))

    labels["section"] = "exec"
    while True:
        DAEMON.labels(status="items-ok", **labels).set(0)
        DAEMON.labels(status="items-ko", **labels).set(0)
        for api_key in conf.apikeys:
            try:
                collect(api_key)
            except Exception:
                DAEMON.labels(status="items-ko", **labels).inc()
                continue
            DAEMON.labels(status="items-ok", **labels).inc()
        DAEMON.labels(status="loop-count", **labels).inc()
        time.sleep(conf.loop.interval)


if __name__ == "__main__":
    start_http_server(conf.prometheus.port)
    main()
