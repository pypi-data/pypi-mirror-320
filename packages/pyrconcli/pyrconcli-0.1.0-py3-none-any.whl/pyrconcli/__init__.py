from prompt_toolkit import PromptSession, print_formatted_text, ANSI
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
import argparse
import mcrcon
import os


def minecraft_colors_to_ansi(text):
    color_dict = {
        "§0": "\u001b[30m",
        "§1": "\u001b[34m",
        "§2": "\u001b[32m",
        "§3": "\u001b[36m",
        "§4": "\u001b[31m",
        "§5": "\u001b[35m",
        "§6": "\u001b[33m",
        "§7": "\u001b[37m",
        "§8": "\u001b[30;1m",
        "§9": "\u001b[34;1m",
        "§a": "\u001b[32;1m",
        "§b": "\u001b[36;1m",
        "§c": "\u001b[31;1m",
        "§d": "\u001b[35;1m",
        "§e": "\u001b[33;1m",
        "§f": "\u001b[37;1m",
    }
    for key, value in color_dict.items():
        text = text.replace(key, value)
    return text.replace("\n", "\u001b[0m\n")


completer = NestedCompleter.from_nested_dict(
    {
        "attribute": None,
        "advancement": {"grant": None, "revoke": None},
        "ban": None,
        "ban-ip": None,
        "banlist": {"ips": None, "players": None},
        "bossbar": {
            "add": None,
            "get": None,
            "list": None,
            "remove": None,
            "set": None,
        },
        "clear": None,
        "clone": None,
        "data": {
            "get": {"block": None, "entity": None, "storage": None},
            "merge": {"block": None, "entity": None, "storage": None},
            "modify": {"block": None, "entity": None, "storage": None},
            "remove": {"block": None, "entity": None, "storage": None},
        },
        "datapack": {"disable": None, "enable": None, "list": None},
        "defaultgamemode": {
            "adventure": None,
            "creative": None,
            "spectator": None,
            "survival": None,
        },
        "deop": None,
        "difficulty": None,
        "effect": {"clear": None, "give": None},
        "enchant": None,
        "experience": {"add": None, "set": None, "query": None},
        "xp": {"add": None, "set": None, "query": None},
        "list": None,
        "help": None,
        "gamemode": {
            "adventure": None,
            "creative": None,
            "spectator": None,
            "survival": None,
        },
        "time": {
            "add": None,
            "query": {"daytime": None, "gametime": None, "day": None},
            "set": {"day": None, "night": None, "noon": None, "midnight": None},
        },
    }
)


def main():
    parser = argparse.ArgumentParser(
        prog="pyrconcli",
        description="a better terminal interface for minecraft rcon",
    )
    parser.add_argument("ip", type=str, help="ip adresss of server")
    parser.add_argument("password", type=str, help="password for rcon protocol")
    parser.add_argument(
        "-P",
        type=int,
        help="rcon port (default is 25575)",
        default=25575,
        dest="port",
    )
    args = parser.parse_args()
    history_file = "~/.pyrconcli_prompt_history"
    try:
        open(os.path.expanduser(history_file), "a+").close()
    except FileNotFoundError:
        open(os.path.expanduser(history_file), "w+").close()

    with mcrcon.MCRcon(args.ip, args.password, args.port) as rcon:
        session = PromptSession(
            "rcon@{}> ".format(args.ip),
            history=FileHistory(os.path.expanduser(history_file)),
        )
        try:
            print("type 'exit' or press crtl-d to exit")
            command = session.prompt(
                completer=completer, auto_suggest=AutoSuggestFromHistory()
            )
            while command != "exit":
                resp = rcon.command(command)
                resptext = minecraft_colors_to_ansi(resp)
                print_formatted_text(ANSI(resptext))
                command = session.prompt(
                    auto_suggest=AutoSuggestFromHistory(), completer=completer
                )
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
