#!/bin/bash
set -e

REPO="inogai/zmk-config"
ARTIFACTS_DIR="./artifacts"
FIRMWARE_DIR="./firmware"

echo "Fetching latest workflow run..."
RUN_ID=$(gh run list --repo "$REPO" --workflow=build.yml --status=success --limit=1 --json databaseId --jq '.[0].databaseId')

if [ -z "$RUN_ID" ]; then
    echo "No successful workflow runs found"
    exit 1
fi

echo "Latest successful run: $RUN_ID"

rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

echo "Downloading artifacts..."
gh run download "$RUN_ID" --repo "$REPO" --dir "$ARTIFACTS_DIR"

rm -rf "$FIRMWARE_DIR"
mkdir -p "$FIRMWARE_DIR"

echo "Extracting UF2 files..."
find "$ARTIFACTS_DIR" -name "*.uf2" -exec cp {} "$FIRMWARE_DIR/" \;

echo ""
echo "Firmware files copied to $FIRMWARE_DIR/:"
ls -lh "$FIRMWARE_DIR"

echo ""
echo "Done! Flash with:"
echo "  Left:  cp $FIRMWARE_DIR/lily58_left-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/"
echo "  Right: cp $FIRMWARE_DIR/lily58_right-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/"
