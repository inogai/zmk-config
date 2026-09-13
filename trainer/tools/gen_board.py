import argparse, json, os, re, sys
"""gen_board.py — generate layer-tutor board JS from the ZMK keymap (inogai/zmk-config Lily58).

Usage:
用法通常走 Justfile：zmk-config root 下 `just trainer-gen` 輸出到 repos/layer-tutor。
直接跑：python3 trainer/tools/gen_board.py -o ../repos/layer-tutor/typing-tutor/js/boards/lily58.js

Reads the BASE + NAV layers and emits the board file layer-tutor consumes:
per-key legends (slot 0 = BASE tap char, slot 1 = NAV action), the NAV hold
key (tap-comma), the shift key, space key, and a per-key position map.
Re-run after any keymap change so the trainer follows the real layout.
"""
import argparse, json, os, re, sys

KP_LEGEND = {}
KP_LEGEND.update((c, c) for c in "QWERTYUIOPASDFGHJKLZXCVBNM")
KP_LEGEND.update(N1="1", N2="2", N3="3", N4="4", N5="5",
                 N6="6", N7="7", N8="8", N9="9", N0="0",
                 MINUS="-", EQUAL="=", COMMA=",", DOT=".", SLASH="/", SEMI=";", QUOTE="'",
                 LBRC="[", RBRC="]", BSLH="\\", GRAVE="`", LBKT="[", RBKT="]",
                 AMPS="&", ASTRK="*", LPAR="(", RPAR=")", TILDE="~", EXCL="!", AT="@",
                 HASH="#", PIPE="|", DLLR="$", PRCNT="%", CARET="^", PLUS="+", COLON=":", UNDER="_",
                 LEFT="\u2190", DOWN="\u2193", UP="\u2191", RIGHT="\u2192",
                 HOME="\u21e4", END="\u21e5", PG_UP="\u21d1", PG_DN="\u21d3")
KP_LEGEND.update(ESC="Esc", TAB="Tab", SPACE="Space", RET="Ret", BSPC="Bspc", DEL="Del",
                 LSHFT="Shift", RSHFT="Shift", LCTRL="Ctrl", RCTRL="Ctrl",
                 LALT="Alt", RALT="Alt", LGUI="Win", RGUI="Win", CAPS="Caps")

ROW_SPLITS = [(6, 6), (6, 6), (6, 6), (6, 8), (3, 5)]   # left,right token counts per row
ROW_NAMES = ["number", "upper", "home", "lower", "thumb"]
AVOID = {"trans", "none", "bootloader"}


def strip_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def layer_blocks(text):
    blocks = {}
    for m in re.finditer(r"^\s*(BASE|NAV)\s*\{$", text, re.M):
        name = m.group(1)
        i = m.end()
        depth = 1
        while depth and i < len(text):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        blocks[name] = text[m.start():i]
    return blocks


def units_in(block):
    m = re.search(r"bindings\s*=\s*<(.*?)>\s*;", block, re.S)
    if not m:
        sys.exit("no bindings block found")
    units, cur = [], None
    for tok in m.group(1).split():
        if tok.startswith("&"):
            cur = [tok]
            units.append(cur)
        elif cur is not None:
            cur.append(tok)
        else:
            units.append([tok])
    return units


def legend_of(unit):
    """Return (slot0 legend or None, hold-layer name or None)."""
    if not unit or not unit[0].startswith('&'):
        return None, None
    kind = unit[0][1:]
    if kind in AVOID:
        return None, None
    args = unit[1:]
    if kind == "kp":
        return KP_LEGEND.get(args[0]) if args else None, None
    if kind in ("u_lt", "lt"):
        if len(args) >= 2:
            hold = args[0] if args[0].startswith('U_') else None
            return KP_LEGEND.get(args[-1]), hold
        return None, None
    if kind in ("u_mt", "mt", "u_mt_gui_esc"):
        return KP_LEGEND.get(args[-1]) if args else None, None
    return None, None

def main():
    ap = argparse.ArgumentParser()
    HERE = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("keymap", nargs="?", default=os.path.join(HERE, "..", "..", "config", "lily58.keymap"))
    ap.add_argument("-o", "--out", nargs="?", default=os.path.join(HERE, "..", "typing-tutor", "js", "boards", "lily58.js"))
    a = ap.parse_args()

    text = strip_comments(open(a.keymap, encoding="utf-8").read())
    blocks = layer_blocks(text)
    missing = {"BASE", "NAV"} - set(blocks)
    if missing:
        sys.exit("missing layers: %s" % sorted(missing))

    base = [legend_of(u) for u in units_in(blocks['BASE'])]
    nav = [legend_of(u) for u in units_in(blocks['NAV'])]
    if len(base) != len(nav):
        sys.exit("unit count mismatch: BASE=%d NAV=%d" % (len(base), len(nav)))
    expect = sum(l + r for l, r in ROW_SPLITS)
    if len(base) != expect:
        sys.exit("BASE has %d bindings, expected %d (Lily58)" % (len(base), expect))

    left_rows, right_rows = [], []
    layer_hold, shift_ids, space_id = {}, [], None
    idx = 0
    for (l_n, r_n) in ROW_SPLITS:
        lrow, rrow = [], []
        for c2 in range(l_n):
            gi = idx + c2
            l0, hold = base[gi]
            l1, _ = nav[gi]
            if l0 is None and l1 is None and hold is None:
                continue
            # id column = index among emitted keys, so skipped &none/&trans
            # slots (miryoku bottom-row / thumb padding) don't shift the row.
            key_id = "L%d%d" % (len(left_rows), len(lrow))
            if hold == "U_NAV":
                layer_hold[1] = key_id
            if l0 == "Shift":
                shift_ids.append(key_id)
            if l0 == "Space":
                space_id = key_id
            lrow.append([key_id, l0, l1, None])
        for c2 in range(l_n, l_n + r_n):
            gi = idx + c2
            l0, hold = base[gi]
            l1, _ = nav[gi]
            if l0 is None and l1 is None and hold is None:
                continue
            key_id = "R%d%d" % (len(right_rows), len(rrow))
            if hold == "U_NAV":
                layer_hold[1] = key_id
            if l0 == "Shift":
                shift_ids.append(key_id)
            if l0 == "Space":
                space_id = key_id
            rrow.append([key_id, l0, l1, None])
        left_rows.append(lrow)
        right_rows.append(rrow)
        idx += l_n + r_n

    # ---- geometry (in "u" units) ----
    CO_L = [0.05, 0.15, 0.25, 0.35, 0.35, 0.45]
    CO_R = list(reversed(CO_L))
    positions = {}
    for half, rows in (("L", left_rows), ("R", right_rows)):
        for row_idx in range(4):
            for key in rows[row_idx]:
                col = int(key[0][2:])
                co = CO_L[col] if half == "L" else CO_R[min(col, 5)]
                positions[key[0]] = {"x": col, "y": row_idx + co}
    THUMBS = {
        "L40": {"x": 2.2, "y": 4.25},
        "L41": {"x": 3.35, "y": 4.45},
        "L42": {"x": 4.5, "y": 4.05, "w": 1, "h": 1.5},
        "R40": {"x": 3.0, "y": 4.05, "w": 1, "h": 1.5},
        "R41": {"x": 1.85, "y": 4.25},
        "R42": {"x": 0.7, "y": 4.4},
    }
    for key in left_rows[4] + right_rows[4]:
        if key[0] in THUMBS:
            positions[key[0]] = THUMBS[key[0]]

    def emit(rows, half):
        out = []
        for i in range(5):
            block = ['  [']
            for key in rows[i]:
                block.append('    ' + json.dumps(key, ensure_ascii=False) + ',')
            block.append('  ],')
            out.append('\n'.join(block))
        return out
        out.append('\n'.join(block))

    js = (
        '// Generated by zmk-config/trainer/tools/gen_board.py — DO NOT EDIT BY HAND.\n'
        '// Board: Lily58 (inogai/zmk-config) · slot 0 = BASE, slot 1 = NAV (hold comma).\n'
        "import { createLayout } from './buildLayout.js';\n\n"
        'const XX = null;\n\n'
        'const LEFT = [\n' + '\n'.join(emit(left_rows, 'left')) + '\n];\n\n'
        'const RIGHT = [\n' + '\n'.join(emit(right_rows, 'right')) + '\n];\n\n'
        'const layout = createLayout({\n'
        '  left: LEFT,\n'
        '  right: RIGHT,\n'
        '  layerHold: ' + json.dumps(layer_hold) + ',\n'
        '  shiftKeys: ' + json.dumps(shift_ids) + ',\n'
        '  spaceKeyId: ' + json.dumps(space_id) + ',\n'
        '  shiftedL0: {\n'
        "    ':': ';', '<': ',', '>': '.', '?': '/', '_': '-',\n"
        "    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8',\n"
        "    '(': '9', ')': '0',\n"
        '  },\n'
        '});\n\n'
        '/** @type {ReturnType<typeof createLayout> & { id: string, name: string, productName: string, formFactor: string, description: string, geometry: string, vilPath: null, comingSoon: boolean, homeIds: string[], positions: Record<string, {x:number,y:number,w?:number,h?:number,r?:number}> }} */\n'
        'export const board = {\n'
        "  id: 'lily58',\n"
        "  name: 'Lily58',\n"
        "  productName: 'Lily58 (inogai/zmk-config, Miryoku-style)',\n"
        "  formFactor: '5-row split · 58 keys',\n"
        "  description: 'Lily58 with shifted bottom row (ZXCV/B/comma) and hold-comma NAV layer.',\n"
        "  geometry: 'lily58',\n"
        '  vilPath: null,\n'
        '  comingSoon: false,\n'
        '  homeIds: ' + json.dumps(['L21', 'L22', 'L23', 'L24', 'R20', 'R21', 'R22', 'R23']) + ',\n'
        '  positions: ' + json.dumps(positions) + ',\n'
        '  ...layout,\n'
        '};\n\n'
        'export default board;\n'
    )
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(js)
    print("wrote %s: %d bindings, hold=%s shift=%s space=%s"
          % (a.out, len(base), layer_hold, shift_ids, space_id))


if __name__ == "__main__":
    main()
