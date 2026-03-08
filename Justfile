keyboard := "lily58"

# ── Keymap visualization ──────────────────────────────────────────

parse:
    keymap parse -c 10 -z config/{{ keyboard }}.keymap > gen/{{ keyboard }}_keymap.yaml

draw: parse
    keymap draw gen/{{ keyboard }}_keymap.yaml > gen/{{ keyboard }}_keymap.svg

# Generate per-layer PNGs for the companion app
layer-images: parse
    #!/usr/bin/env bash
    set -euo pipefail
    layers=("Base" "Extra" "Tap" "Button" "Nav" "Mouse" "Media" "Num" "Sym" "Fun" "WM")
    fnames=("base" "extra" "tap" "button" "nav" "mouse" "media" "num" "sym" "fun" "wm")
    for i in "${!layers[@]}"; do
        echo "  ${fnames[$i]}.png"
        keymap draw gen/{{ keyboard }}_keymap.yaml -s "${layers[$i]}" \
            | rsvg-convert -d 192 -p 192 -o "companion/assets/${fnames[$i]}.png"
    done

# ── Firmware ──────────────────────────────────────────────────────

fetch:
    ./fetch-firmware.sh

flash-left: fetch
    cp ./firmware/lily58_left-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/ || true

flash-right: fetch
    cp ./firmware/lily58_right-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/ || true

# ── Keyboard Layers App Companion ─────────────────────────────────

# Run companion app locally (USB)
companion:
    python3 companion/main.py

# Run companion app locally (BLE — requires sudo on macOS)
companion-ble:
    sudo python3 companion/main.py --ble

# Run companion app as web server (USB)
companion-web:
    python3 companion/main.py --web

# Run companion app as web server (BLE — requires sudo on macOS)
companion-web-ble:
    sudo python3 companion/main.py --ble --web
