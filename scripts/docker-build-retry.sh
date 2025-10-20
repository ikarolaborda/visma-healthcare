#!/bin/bash

# Docker Build Retry Script
# Handles transient Docker Hub errors (503, timeouts) with exponential backoff

set -e

MAX_RETRIES=5
RETRY_DELAY=5
BUILD_CMD="docker compose build"

echo "🔧 Docker Build with Retry Mechanism"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for i in $(seq 1 $MAX_RETRIES); do
    echo ""
    echo "📦 Build Attempt $i of $MAX_RETRIES..."

    if $BUILD_CMD; then
        echo ""
        echo "✅ Build successful!"
        exit 0
    else
        EXIT_CODE=$?

        if [ $i -lt $MAX_RETRIES ]; then
            DELAY=$((RETRY_DELAY * i))
            echo ""
            echo "⚠️  Build failed with exit code $EXIT_CODE"
            echo "⏳ Retrying in ${DELAY} seconds..."
            echo "   (This might be due to temporary Docker Hub unavailability)"
            sleep $DELAY
        else
            echo ""
            echo "❌ Build failed after $MAX_RETRIES attempts"
            echo ""
            echo "Common solutions:"
            echo "  1. Wait a few minutes and try again (Docker Hub might be temporarily down)"
            echo "  2. Check your internet connection"
            echo "  3. Try using a Docker Hub mirror or VPN"
            echo "  4. Check Docker Hub status: https://status.docker.com/"
            echo ""
            exit $EXIT_CODE
        fi
    fi
done
