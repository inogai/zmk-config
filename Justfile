keyboard := "eyelash_sofle"
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
    cp ./firmware/eyelash_sofle_left.uf2 /Volumes/NICENANO/ || true

flash-right: fetch
    cp ./firmware/eyelash_sofle_right.uf2 /Volumes/NICENANO/ || true


# ── Trainer ─────────────────────────────────────────────────────

# Emit Eyelash Sofle board declaration for layer-tutor (BOARD_INPUT.md).
# Override OUT to point at a local layer-tutor checkout.
trainer-gen OUT="../repos/layer-tutor/typing-tutor/js/boards/eyelash-sofle.js":
    python3 trainer/tools/gen_board_eyelash.py -o {{OUT}} --json trainer/boards/eyelash-sofle.json

trainer-serve:
    cd ../repos/layer-tutor/typing-tutor && python3 -m http.server 8000
