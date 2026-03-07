keyboard := "lily58"

parse:
    keymap parse -c 10 -z config/{{ keyboard }}.keymap > gen/{{ keyboard }}_keymap.yaml 

draw: parse
    keymap draw gen/{{ keyboard }}_keymap.yaml > gen/{{ keyboard }}_keymap.svg
