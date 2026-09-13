# trainer — 打字練習（Layer Tutor fork，適配 Lily58 ZMK keymap）

fork 自 [thebiglaskowski/layer-tutor](https://github.com/thebiglaskowski/layer-tutor)（MIT）。
瀏覽器 PWA、零依賴、無 build step。課程與鍵盤圖全部由**真實 keymap**生成：
即 config/lily58.keymap 的 BASE + NAV 兩層。

## 跑起來（你的機器上）

    cd ../repos/layer-tutor/typing-tutor
    python3 -m http.server 8000
    # 瀏覽器開 http://localhost:8000
    #（或直接嗂到服役中的 http://192.168.70.100:20000/）
## 改過 keymap 之後重新生成 board

    cd ..   # zmk-config root
    just trainer-gen                      # keymap → ../repos/layer-tutor/.../js/boards/lily58.js
    cd ../repos/layer-tutor/typing-tutor && node --test tests/*.test.js   # 全測試
## 課程設計（typing.com 式高重複，對齊實際鍵位）

| Stage | 內容 | 練什麼 |
|---|---|---|
| home-row | ASDF/HJKL（位置沒變） | 暖身 + 基線 |
| bottom-left | Z X C V（各右移一格） | 下排左新肌肉記憶 |
| bottom-right | B（右 index 內位）N M（順移） | 下排右新肌肉記憶 |
| punctuation-shift | , . / ; - + shift 對（< > ? : _） | tap 逗號（NAV 觸發鍵）與 shift 組合 |
| sentences | 真實短句/全字母句 | 全 BASE 綜合 |
| nav-arrows | hold 逗號 + HJKL（←↓↑→） | NAV 層方向鍵 |
| nav-paging | hold 逗號 + HOME/END/PG_UP/PG_DN（B N M . 位） | NAV 層翻頁 |
| hold-drill | hold 逗號跨整段：左手照常打字 + 右手導航 | LHS 穿透混搭 = 真實編輯手感 |

板載機制：NAV 由逗號鍵觸發（tap 逗號 / hold NAV）——trainer 的 layer-1 就是 NAV，
hold badge 顯示「HOLD ,」；shift = LSHFT（左 home pinky）；space = 左內拇指。
按錯鍵會閃你實際按到的物理鍵；游標只在正確輸入時前進；≥90% 正確率解鎖下一關。

## 目錄

    trainer/
    ├── tools/gen_board.py  # keymap → board JS 生成器（改 keymap 後重跑，產物寫進 repos/layer-tutor）
    ├── LICENSE         # MIT（layer-tutor 原檔）
    ├── AGENTS.md       # 上游原檔（repo 才是真源）
    └── README.md       # 本文件

    PWA 本體（typing-tutor/ 課程/測試）住在 ../repos/layer-tutor/typing-tutor —— repo = 唯一家。
