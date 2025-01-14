# pyRconcli

A usable minecraft rcon terminal interface made with prompt_toolkit and mcrcon.

## Features:

- Suggestions
- Color support (might depend on your terminal)
- Emacs keybinds (just like every other console)

## How to use:

Just run it like so:
```
./main.py <host> <password>
```

If your server uses diffrent port for rcon you can specify it like so:

```
./main.py <host> <password> -P <port_number>
```

Press crtl-d or crtl-c or just type `exit` to terminate your connection.

## TODO:

- more suggestions
- dynamic suggestions for players?
- package for pypi for easier instalation
