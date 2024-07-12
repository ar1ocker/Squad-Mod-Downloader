# Squad-Mod-Downloader
Simple script for downloading mods for a Squad game server

## Usage

```
mod_downloader.py [-h] -g GAME [-s STEAM] [--number-of-downloads NUMBER_OF_DOWNLOADS] [-d] [-c] [mods ...]

positional arguments:
  mods                  list of mod ids (if you need to download)

optional arguments:
  -h, --help            show this help message and exit
  -g GAME, --game GAME  path to game server directory
  -s STEAM, --steam STEAM
                        path to steam cmd
  --number-of-downloads NUMBER_OF_DOWNLOADS
                        how many times will each mod be downloaded, to bypass the bug with downloading
  -d, --dry             running the script without actually performing any actions
  -c, --clear-mods      remove old mods from the game folder
```

The list of mods is optional, you can simply delete all mods using the command 

```sh
mod_downloader.py -g <game_server_path> --clear-mods
```
