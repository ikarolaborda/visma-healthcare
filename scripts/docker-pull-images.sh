#!/bin/bash

# Pre-pull Docker images to avoid 503 errors during build
# This script pulls base images separately with retry logic

set -e

IMAGES=(
    "node:20-alpine"
    "nginx:1.25-alpine"
    "python:3.11-slim"
)

MAX_RETRIES=3
RETRY_DELAY=10

echo "🔍 Pre-pulling Docker base images..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for IMAGE in "${IMAGES[@]}"; do
    echo "📥 Pulling $IMAGE..."

    for i in $(seq 1 $MAX_RETRIES); do
        if docker pull "$IMAGE"; then
            echo "   ✅ Successfully pulled $IMAGE"
            echo ""
            break
        else
            if [ $i -lt $MAX_RETRIES ]; then
                echo "   ⚠️  Pull failed, retrying in ${RETRY_DELAY}s... (Attempt $i/$MAX_RETRIES)"
                sleep $RETRY_DELAY
            else
                echo "   ❌ Failed to pull $IMAGE after $MAX_RETRIES attempts"
                echo ""
                echo "Troubleshooting steps:"
                echo "  1. Check Docker Hub status: https://status.docker.com/"
                echo "  2. Wait a few minutes and try again"
                echo "  3. Check your network connection"
                echo "  4. Try using: docker login (if you have rate limit issues)"
                echo ""
                exit 1
            fi
        fi
    done
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All base images pulled successfully!"
echo "   You can now run: make build"
echo ""
