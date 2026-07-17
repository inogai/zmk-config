keyboard := "lily58"
config := "keymap-config.yaml"

# ── Keymap visualization ──────────────────────────────────────────

parse:
    keymap -c {{ config }} parse -c 10 -z config/{{ keyboard }}.keymap > gen/{{ keyboard }}_keymap.yaml

draw: parse
    keymap -c {{ config }} draw gen/{{ keyboard }}_keymap.yaml > gen/{{ keyboard }}_keymap.svg

# ── Firmware ──────────────────────────────────────────────────────

fetch:
    ./fetch-firmware.sh

flash-left: fetch
    cp ./firmware/lily58_left-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/ || true

flash-right: fetch
    cp ./firmware/lily58_right-nice_nano_v2-zmk.uf2 /Volumes/NICENANO/ || true

