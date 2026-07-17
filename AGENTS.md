# AGENTS.md

## Overview

This is a [ZMK](https://zmk.dev/) keyboard firmware configuration repository for a **Lily58** split keyboard using **nice!nano v2** controllers. The keymap is Miryoku-inspired with **Colemak-DH** as the default alpha layout, plus a QWERTY fallback layer.

## Repository Structure

```
.
├── config/                  # ZMK firmware configuration
│   ├── west.yml             # Zephyr west manifest (pins ZMK v0.3)
│   ├── lily58.keymap        # Main keymap (devicetree, ~700 lines)
│   └── lily58.conf          # Board Kconfig fragment (mouse keys, encoders, display)
├── boards/shields/          # Custom ZMK shields directory (currently empty)
├── zephyr/module.yml        # Zephyr module metadata
├── build.yaml               # GitHub Actions build matrix
├── keymap-config.yaml       # Keymap-drawer visualization config (glyphs, keycode mappings)
├── Justfile                 # Task runner (parse, draw, flash)
├── flake.nix                # Nix dev shell (just, keymap-drawer)
├── fetch-firmware.sh        # Downloads latest firmware artifacts via `gh` CLI
└── .github/workflows/build.yml  # CI: builds firmware on push/PR via zmkfirmware/zmk
```

## Keymap Design

### Layers (11 total)

| Index | Name     | Purpose |
|-------|----------|---------|
| 0     | Base     | Colemak-DH alphas with home-row mods |
| 1     | Extra    | QWERTY alphas with home-row mods |
| 2     | Tap      | Colemak-DH without hold-taps (for gaming / passthrough) |
| 3     | Button   | Clipboard (Mac: Cmd+C/V/X/Z) + mouse buttons (mirrored) |
| 4     | Nav      | Navigation (arrows, home/end, pgup/pgdn, ins) + layer switching |
| 5     | Mouse    | Mouse movement + scroll wheel |
| 6     | Media    | Media keys, Bluetooth profile select, output toggle, bootloader |
| 7     | Num      | Number pad layout |
| 8     | Sym      | Symbols layout |
| 9     | Fun      | Function keys (F1-F12) + Print Screen / Scroll Lock / Pause |
| 10    | WM       | AeroSpace window manager shortcuts (macOS, Left Alt combos) |

### Custom Behaviors

- **`u_mt`** — Hold-tap for mod keys (tap-preferred, 250ms tapping term, 120ms prior-idle). Used for home-row mods.
- **`u_lt`** — Hold-tap for layer keys (tap-preferred, 250ms). Hold = momentary layer, tap = keypress.
- **`u_to_U_*`** — Tap-dance guards: require double-tap to activate `&to <layer>`. Prevents accidental layer locks.
- **`u_bt_sel_*`** — Mod-morph: tap = select Bluetooth profile, shift+tap = select then clear (disconnect).
- **`u_out_tog`** — Mod-morph: tap = toggle output, shift+tap = force USB.
- **`u_caps_word`** — Mod-morph: tap = caps word, shift+tap = CAPS lock.

### Key Design Decisions

- **Mac-first**: Clipboard shortcuts use Cmd (LGUI), not Ctrl. WM layer targets AeroSpace on macOS.
- **No top number row**: Miryoku-style — numbers are on the Num layer, symbols on Sym, F-keys on Fun.
- **Double-tap layer lock**: All `&to` layer switches require a double-tap to prevent accidental activation.
- **Shift-functions**: Bluetooth profile clear, output force-USB, and caps lock are accessed via shift-modified taps.
- **Mouse keys**: Movement acceleration tuned (exponent 1, 1500ms to max speed, 0ms delay).

## Build System

### CI (GitHub Actions)

On every push and PR, GitHub Actions builds firmware for both halves:
- **Left**: `nice_nano_v2` + `lily58_left` shield, with ZMK Studio snippet
- **Right**: `nice_nano_v2` + `lily58_right` shield

The workflow uses `zmkfirmware/zmk/.github/workflows/build-user-config.yml@v0.3`.

### Local Development

A Nix flake provides the development environment. Run `direnv allow` (or `nix develop`) to enter the shell.

**Keymap visualization** (via `just`):
```
just parse          # Parse keymap → gen/lily58_keymap.yaml
just draw           # Generate SVG keymap diagram
```

**Firmware**:
```
just fetch          # Download latest firmware artifacts from CI
just flash-left     # Flash left half (copies UF2 to NICENANO volume)
just flash-right    # Flash right half
```

## Keymap Editing Workflow

1. Edit `config/lily58.keymap` — the single source of truth for the keymap
2. Run `just parse` to validate and generate the parsed YAML
3. Run `just draw` to visualize changes as SVG
4. Commit and push — CI builds the firmware
5. Run `just fetch` to download the built UF2 files
6. Run `just flash-left` / `just flash-right` to flash

## Important Notes

- **The keymap is self-contained** — it does not `#include` external Miryoku headers. All behaviors, macros, and layer definitions are defined inline in `lily58.keymap`.
- **`lily58.keymap.bak`** is an older keymap backup using different hold-tap behaviors (`hl`/`hr` with `hold-trigger-on-release`). It is not used in builds.
- **ZMK Studio** is enabled on the left half via the `studio-rpc-usb-uart` snippet.
- **Mouse keys and encoders** are configured in `lily58.conf` but currently commented out (the physical Lily58 has no encoders by default).
- **Generated files** (`gen/`, `.zmk/`) are gitignored.
