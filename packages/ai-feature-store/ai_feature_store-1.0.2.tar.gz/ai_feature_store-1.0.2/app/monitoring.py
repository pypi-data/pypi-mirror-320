from prometheus_client import start_http_server, Counter

REQUEST_COUNT = Counter('feature_requests', 'Number of feature requests')

def init_monitoring(port=8001):
    start_http_server(port)

def increment_request_count():
    REQUEST_COUNT.inc()
