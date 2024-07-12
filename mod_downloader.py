#!/bin/env python3
"""
Script for downloading mods to the squad server
"""

import argparse
import pathlib
import shutil
import subprocess
from typing import Union

_parser = argparse.ArgumentParser()
_parser.add_argument("mods", help="list of mod ids (if you need to download)", type=int, nargs="*")
_parser.add_argument("-g", "--game", required=True, help="path to game server directory", type=pathlib.Path)
_parser.add_argument("-s", "--steam", help="path to steam cmd", default="/usr/games/steamcmd", type=pathlib.Path)
_parser.add_argument(
    "--number-of-downloads",
    help="how many times will each mod be downloaded, to bypass the bug with downloading",
    type=int,
    default=2,
)
_parser.add_argument(
    "-d", "--dry", help="running the script without actually performing any actions", action="store_true"
)
_parser.add_argument(
    "-c", "--clear-mods", dest="clear_mods", help="remove old mods from the game folder", action="store_true"
)


def _parse_args() -> argparse.Namespace:
    args: argparse.Namespace = _parser.parse_args()
    error_found = False
    errors: list[str] = []

    if not args.game.exists() or not args.game.is_dir() or not args.game.is_absolute():
        errors.append(f"[!] '{args.game}' is not dir, or not exists, or path is not absolute")
        error_found = True

    if not args.steam.exists() or not args.steam.is_file() or not args.steam.is_absolute():
        errors.append(f"[!] '{args.steam}' is not file, or not exists, or path is not absolute")
        error_found = True

    if error_found:
        for error_text in errors:
            print(error_text, flush=True)
        exit(1)

    return args


def _rmtree(path: Union[str, pathlib.Path], dry: bool) -> None:
    print(f"[+] Remove directory '{path}'", flush=True)

    if not dry:
        shutil.rmtree(path, ignore_errors=True)


def _copytree(path_from: Union[str, pathlib.Path], path_to: Union[str, pathlib.Path], dry: bool) -> None:
    print(f"[+] Copy '{path_from}' to '{path_to}'", flush=True)

    if not dry:
        shutil.copytree(path_from, path_to)


def run_downloading(
    steamcmd_path: Union[str, pathlib.Path], gamedir_path: Union[str, pathlib.Path], mod_id: str, dry: bool
) -> None:
    """Launches steam to download mods to the folder with the game server

    Args:
        steamcmd_path (str | pathlib.Path): the path to the steam executable file
        gamedir_path (str | pathlib.Path): the path to the root folder of the game server
        mod_id (str): mod id
        dry (bool): without actually starting
    """

    print(f"\n[+] The beginning of downloading the mod {mod_id}", flush=True)

    if not dry:
        subprocess.run(
            [
                steamcmd_path,
                "+login",
                "anonymous",
                "+force_install_dir",
                gamedir_path,
                "+workshop_download_item",
                "393380",
                mod_id,
                "validate",
                "+quit",
            ]
        )


def clear_mods(gamedir_path: pathlib.Path, dry: bool) -> None:
    mods_in_server_folder: pathlib.Path = gamedir_path / "SquadGame/Plugins/Mods/"

    print("[+] Clear mods in game", flush=True)

    for path in mods_in_server_folder.iterdir():
        if (
            path.is_dir()
            and path.is_absolute()
            and path.parts[-1].isdigit()
            and not path.is_symlink()
            and not path.is_mount()
        ):
            _rmtree(path, dry)


def install_mods(
    mods: list[int],
    steamcmd_path: pathlib.Path,
    gamedir_path: pathlib.Path,
    number_of_downloads: int,
    dry: bool,
) -> None:
    """Installs mods on the squad game server

    Args:
        mods (list[int]): list of mods
        steamcmd_path (pathlib.Path): the path to the steam executable file
        gamedir_path (pathlib.Path): the path to the root folder of the game server
        number_of_downloads (int): how many times will each mod be downloaded, to bypass the bug with downloading
        dry (bool): without actually starting
    """
    for mod in mods:
        mod_in_steam_path = gamedir_path / "steamapps/workshop/content/393380/" / str(mod)
        mod_in_server_path: pathlib.Path = gamedir_path / "SquadGame/Plugins/Mods/" / str(mod)

        _rmtree(mod_in_steam_path, dry)

        # steamcmd иногда багует и не до конца скачивает мод, рапортуя при этом об удачном скачивании.
        # Решаем эту проблему скачивая несколько раз
        for attempt in range(number_of_downloads):
            print(f"\n[+] attempt {attempt + 1} - Mod number '{mod}' is being downloaded", flush=True)
            run_downloading(steamcmd_path, gamedir_path, str(mod), dry)

        _rmtree(mod_in_server_path, dry)

        _copytree(mod_in_steam_path, mod_in_server_path, dry)


def _main() -> None:
    args: argparse.Namespace = _parse_args()

    if args.clear_mods:
        clear_mods(args.game, args.dry)

    if args.mods:
        install_mods(args.mods, args.steam, args.game, args.number_of_downloads, args.dry)


if __name__ == "__main__":
    _main()
