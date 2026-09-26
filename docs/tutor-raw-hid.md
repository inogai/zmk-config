# Spike: Raw HID for layer-tutor (D1–2)

Branch-only firmware spike. Enables **zzeneg/zmk-raw-hid** on the **left (USB central)** build so macOS can enumerate a vendor Raw HID interface alongside Studio CDC and Boot Keyboard. Does **not** yet mute typing or capture keys (`tutor_practice` is a follow-up).

Design docs (host protocol / module plan): `layer-tutor-native` → `docs/PROTOCOL.md`, `docs/ZMK_MODULE.md`, `docs/SPIKE.md`.

## What changed

| File | Change |
|------|--------|
| `config/west.yml` | Add `zzeneg` remote; pin `zmk-raw-hid` to commit `6a37765dfab6197292e7a9f47305dcf87386d56a` (post “pin zmk v0.3” + USB DMA buffer fix) |
| `build.yaml` | Left only: append shield `raw_hid_adapter` (sets `CONFIG_RAW_HID=y`, `CONFIG_USB_HID_DEVICE_COUNT=2`) |
| Right / reset | Unchanged — no Raw HID |

Studio on left is preserved: `studio-rpc-usb-uart` + `CONFIG_ZMK_STUDIO=y` / `CONFIG_ZMK_STUDIO_LOCKING=n`.

Defaults from the module (confirm after flash):

| Setting | Value |
|---------|-------|
| Usage Page | `0xFF60` |
| Usage | `0x61` |
| Report size | 32 bytes |
| Device name | `HID_1` |

Expected nice!nano VID/PID filter (confirm on device): `0x1D50` / `0x615E`. Always open by usage page/usage; never open Boot Keyboard.

## Flash left

1. Push this branch (or open the draft PR) so GitHub Actions runs `zmkfirmware/zmk` `build-user-config` @ `v0.3`.
2. Download the `eyelash_sofle_left` UF2 artifact from the workflow run.
3. Or locally: `just fetch` then flash as usual:

```bash
just flash-left   # Mac: /Volumes/NICENANO
```

Do **not** flash a Raw-HID-enabled UF2 to the right half for this spike.

## Enumerate on macOS

After replug left USB:

1. **System Information → USB / HID** — look for an extra HID interface besides Boot Keyboard / consumer.
2. Or with Python `hidapi` / any Raw HID tool, list devices and filter:

   - Usage Page `0xFF60`, Usage `0x61`
   - Prefer matching VID/PID above once confirmed

3. Open **only** that Raw HID path (32-byte reports).

### Studio coexistence caveat

Composite layout for this spike:

| Interface | Role |
|-----------|------|
| CDC USB UART (`studio-rpc-usb-uart`) | ZMK Studio RPC — keep using Studio as before |
| `HID_0` | Boot Keyboard (+ pointing/consumer as configured) — normal typing still works in D1–2 |
| `HID_1` | Raw HID practice channel — present but inert until a consumer module / host app talks to it |

Smoke-check after flash: keyboard still types, Studio still connects, Raw HID enumerates. If Studio or typing breaks, bisect by rebuilding **without** `raw_hid_adapter` on the same Cormoran pin.

## Host ping expectations (D1–2)

With Raw HID alone and **no** `tutor_practice` listener yet:

- Host may send a 32-byte OUT (e.g. magic `0x54`, version `1`, type `3` = ping per PROTOCOL.md).
- Firmware **will not** reply with a tutor ack until the practice module lands.
- Goal of this spike: confirm the interface exists and can be opened; log any IN (likely none).

Next hardware steps (D3+): ping/ack + enter/exit practice + mute Boot Keyboard — see SPIKE.md.

## Local validation without hardware

This Linux box typically lacks the full Zephyr/ZMK SDK. Validation done on the branch:

- YAML parse of `config/west.yml` and `build.yaml`
- Manifest documents the pin SHA and left-only shield

UF2 production build remains **GitHub Actions** on push/PR (same workflow as main).

## Out of scope (this PR)

- `tutor_practice` capture / mute / fail-safe
- Key bindings or keymap edits
- Right half / BLE Raw HID
- Merging to `main` before hardware smoke-test
