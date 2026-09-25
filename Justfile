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

# 重建 board（讀 config/lily58.keymap → 寫入 repo layer-tutor 的 board JS）
trainer-gen:
    python3 trainer/tools/gen_board.py -o ../repos/layer-tutor/typing-tutor/js/boards/lily58.js

trainer-serve:
    cd ../repos/layer-tutor/typing-tutor && python3 -m http.server 8000
