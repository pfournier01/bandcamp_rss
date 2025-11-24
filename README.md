# Bandcamp feed generator

This script provides a list of ATOM 2.0 formatted feeds tracking the releases of artists followed by a given user.

## Installation
> Tested with Python 3.11. Dependencies are `beautifulsoup4` and `requests`. Versions are specified in `requirements.txt`.

### Easy install [TODO]
Run `install.sh` and follow the prompt.

### Manual install

1. Make sure the dependencies are satisfied.
2. Edit `bandcamp_rss.service_template` and `run.sh_template` to fill in the fields in curly brackets with your relevant information. Once filled in, remove `_template` from the extension.
3. Install the systemd units:
```sh
    systemctl --user enable /location/to/bandcamp_rss.service
    systemctl --user enable /location/to/bandcamp_rss.timer
    systemctl --user start bandcamp_rss.service
```
4. (Optionnal) Run the script once to initialize it: `run.sh`

## Uninistall

### Easy uninstall [TODO]
Run `uninstall.sh` and follow the prompt.

### Manual uninstall
1. Deactivate the systemd units:
```sh
    systemctl --user stop bandcamp_rss.service
    systemctl --user disable bandcamp_rss.service
    systemctl --user disable bandcamp_rss.timer
```
2. Delete the database file.
3. (Optional) Delete the `.atom` files.
4. Delete this folder.

## Usage
Once installed, no manual intervention should be needed, the systemd unit does all the job. If you want to run it manually, you can simply execute the `run.sh` script.

By default, the script runs daily. If you wish to change the frequency, please edit the `bandcamp_rss.timer` file.

