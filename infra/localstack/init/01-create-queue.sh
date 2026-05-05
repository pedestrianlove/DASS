#!/bin/sh
set -eu

awslocal sqs create-queue --queue-name dass-tasks >/dev/null 2>&1 || true
