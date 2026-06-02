"""SQS + Worker fleet exporter for LocalStack, Kubernetes, and Docker.

Polls every N seconds:
- LocalStack SQS queue attributes -> dass_sqs_messages_* gauges
- Kubernetes worker pods when running in-cluster
- Docker daemon for worker containers as a fallback for local compose

Metrics exposed at :9100/metrics.
"""
from __future__ import annotations

import logging
import os
import time

import boto3
import botocore.exceptions
import docker
from docker.errors import DockerException
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from kubernetes.client import ApiException
from prometheus_client import Counter, Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sqs-exporter")

# ── SQS metrics ──────────────────────────────────────────────────────────────
QUEUES = [
    "dass-tasks",
    "dass-tasks-normal",
    "dass-tasks-scheduled",
    "dass-tasks-retry",
]

visible = Gauge("dass_sqs_messages_visible", "Visible SQS messages", ["queue"])
not_visible = Gauge("dass_sqs_messages_not_visible", "In-flight SQS messages", ["queue"])
delayed = Gauge("dass_sqs_messages_delayed", "Delayed SQS messages", ["queue"])
sqs_errors = Counter("dass_sqs_collect_errors_total", "Errors while polling SQS", ["queue"])

# ── Worker fleet metrics ─────────────────────────────────────────────────────
workers_total = Gauge("dass_workers_total", "Total running worker containers")
workers_autoscaled = Gauge("dass_workers_autoscaled", "Autoscaled worker containers only (excludes baseline)")
worker_errors = Counter("dass_workers_collect_errors_total", "Errors polling Docker for workers")


def make_sqs_client():
    return boto3.client(
        "sqs",
        region_name=os.environ.get("DASS_AWS_REGION", "us-east-1"),
        endpoint_url=os.environ.get("DASS_SQS_ENDPOINT_URL", "http://localstack:4566"),
        aws_access_key_id=os.environ.get("DASS_AWS_ACCESS_KEY_ID", "dass"),
        aws_secret_access_key=os.environ.get("DASS_AWS_SECRET_ACCESS_KEY", "dass"),
    )


def make_docker_client():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        log.warning("Docker not reachable: %s — worker metrics will stay at 0", e)
        return None


def make_kubernetes_client():
    if not os.environ.get("KUBERNETES_SERVICE_HOST"):
        return None
    try:
        k8s_config.load_incluster_config()
        return k8s_client.CoreV1Api()
    except Exception as e:
        log.warning("Kubernetes API not reachable: %s — falling back to Docker", e)
        return None


def collect_sqs(client) -> None:
    for q in QUEUES:
        try:
            url = client.get_queue_url(QueueName=q)["QueueUrl"]
            attrs = client.get_queue_attributes(
                QueueUrl=url,
                AttributeNames=[
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                    "ApproximateNumberOfMessagesDelayed",
                ],
            )["Attributes"]
            visible.labels(queue=q).set(int(attrs.get("ApproximateNumberOfMessages", 0)))
            not_visible.labels(queue=q).set(int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)))
            delayed.labels(queue=q).set(int(attrs.get("ApproximateNumberOfMessagesDelayed", 0)))
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code", "?")
            log.warning("queue %s ClientError=%s", q, code)
            sqs_errors.labels(queue=q).inc()
        except Exception:
            log.exception("collect_sqs failed for queue=%s", q)
            sqs_errors.labels(queue=q).inc()


def collect_workers(kube_client, docker_client) -> None:
    if kube_client is not None:
        namespace = os.environ.get("DASS_POD_NAMESPACE", "default")
        label_selector = os.environ.get(
            "DASS_WORKER_LABEL_SELECTOR",
            "app.kubernetes.io/name=worker",
        )
        autoscaled_selector = os.environ.get("DASS_AUTOSCALED_WORKER_LABEL_SELECTOR", "")
        try:
            worker_pods = kube_client.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector,
            ).items
            running_workers = [pod for pod in worker_pods if pod.status.phase == "Running"]
            workers_total.set(len(running_workers))

            if autoscaled_selector:
                autoscaled_pods = kube_client.list_namespaced_pod(
                    namespace=namespace,
                    label_selector=autoscaled_selector,
                ).items
                running_autoscaled = [pod for pod in autoscaled_pods if pod.status.phase == "Running"]
                workers_autoscaled.set(len(running_autoscaled))
            else:
                workers_autoscaled.set(0)
            return
        except ApiException:
            log.exception("collect_workers failed via Kubernetes API")
            worker_errors.inc()
        except Exception:
            log.exception("collect_workers failed via Kubernetes API")
            worker_errors.inc()

    if docker_client is None:
        workers_total.set(0)
        workers_autoscaled.set(0)
        return
    try:
        all_workers = docker_client.containers.list(
            filters={"label": ["com.dass.project=dass", "com.dass.service=worker"]}
        )
        autoscaled = [c for c in all_workers if c.labels.get("com.dass.autoscaled") == "true"]
        workers_total.set(len(all_workers))
        workers_autoscaled.set(len(autoscaled))
    except DockerException:
        log.exception("collect_workers failed")
        worker_errors.inc()


def main() -> None:
    start_http_server(9100)
    interval = float(os.environ.get("DASS_SQS_EXPORTER_INTERVAL", "5"))
    log.info("exporter listening on :9100 interval=%.1fs", interval)

    sqs_client = make_sqs_client()
    kubernetes_client = make_kubernetes_client()
    docker_client = make_docker_client()

    while True:
        try:
            collect_sqs(sqs_client)
        except Exception:
            log.exception("collect_sqs loop error — rebuilding client")
            sqs_client = make_sqs_client()
        try:
            collect_workers(kubernetes_client, docker_client)
        except Exception:
            log.exception("collect_workers loop error — rebuilding clients")
            kubernetes_client = make_kubernetes_client()
            docker_client = make_docker_client()
        time.sleep(interval)


if __name__ == "__main__":
    main()
