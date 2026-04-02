#!/bin/bash
# Trigger Google Photos sync workflow manually
# 
# Usage:
#   ./scripts/trigger-photo-sync.sh          # Normal sync
#   ./scripts/trigger-photo-sync.sh --force  # Force re-sync

set -e

REPO="spacecowboyian/oio-brain"
WORKFLOW="sync-google-photos.yml"

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: 'gh' CLI is not installed"
    echo "Install from: https://cli.github.com"
    exit 1
fi

# Parse arguments
FORCE=${1:-false}
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE=true
fi

echo "🔄 Triggering Google Photos sync..."
echo "Repository: $REPO"
echo "Workflow: $WORKFLOW"
echo "Force sync: $FORCE"
echo ""

# Trigger workflow
if gh workflow run "$WORKFLOW" \
    -R "$REPO" \
    -f "force_sync=$FORCE"; then
    echo ""
    echo "✅ Workflow triggered successfully!"
    echo ""
    echo "View workflow run:"
    echo "  https://github.com/$REPO/actions/workflows/$WORKFLOW"
else
    echo "❌ Failed to trigger workflow"
    exit 1
fi
