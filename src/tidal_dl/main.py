#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Main entry point - 100% CLI compatible with original."""

import getopt
import json
import sys

import tidal_dl.aigpy
from tidal_dl import apiKey
from tidal_dl.events import (
    changeApiKey,
    changePathSettings,
    changeQualitySettings,
    changeSettings,
    loginByAccessToken,
    loginByConfig,
    loginByWeb,
    start,
)
from tidal_dl.paths import (
    getProfilePath,
    getTokenPath,
)
from tidal_dl.printf import Printf
from tidal_dl.settings import (
    SETTINGS,
    TOKEN,
)
from tidal_dl.tidal import TIDAL_API


def mainCommand():
    """Handle command-line arguments - 100% compatible with original."""
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvgl:o:q:r:j",
            [
                "help",
                "version",
                "gui",
                "link=",
                "output=",
                "quality=",
                "resolution=",
                "json",
            ],
        )
    except getopt.GetoptError as errmsg:
        Printf.err(
            vars(errmsg)["msg"]
            + ". Use 'tidal-dl -h' for usage."
        )
        return

    link = None
    showGui = False
    json_mode = False
    non_interactive = False

    for opt, val in opts:
        if opt in ("-h", "--help"):
            Printf.usage()
            return
        if opt in ("-v", "--version"):
            Printf.logo()
            return
        if opt in ("-g", "--gui"):
            # GUI removed in refactor
            Printf.err(
                "GUI mode has been removed. Please use command-line interface."
            )
            return
        if opt in ("-l", "--link"):
            link = val
            continue
        if opt in ("-o", "--output"):
            SETTINGS.downloadPath = val
            SETTINGS.save()
            continue
        if opt in ("-q", "--quality"):
            SETTINGS.audioQuality = SETTINGS.getAudioQuality(
                val
            )
            SETTINGS.save()
            continue
        if opt in (
            "-r",
            "--resolution",
        ):
            SETTINGS.videoQuality = SETTINGS.getVideoQuality(
                val
            )
            SETTINGS.save()
            continue
        if opt in ("-j", "--json"):
            json_mode = True
            continue

    # special option: retrieve json data of item
    # can only be used in junction with link option
    if json_mode and link:
        if not loginByConfig(True):
            Printf.err(
                "Login failed. Please authenticate first."
            )
            return
        try:
            etype, obj = (
                TIDAL_API.getByString(
                    link
                )
            )
            output = {
                "type": etype.name,
                "data": tidal_dl.aigpy.model.modelToDict(
                    obj
                ),
            }
            print(
                json.dumps(
                    output, indent=4
                )
            )
            return
        except Exception as e:
            Printf.err(str(e))
        return

    if not tidal_dl.aigpy.path.mkdirs(
        SETTINGS.downloadPath
    ):
        Printf.err(
            "Invalid download path: "
            + SETTINGS.downloadPath
        )
        return

    # note: entrypoint for command line usage (without --json)
    if link is not None:
        if not loginByConfig():
            loginByWeb()
        Printf.info(
            "Download path: "
            + SETTINGS.downloadPath
        )
        start(link)


def main():
    """Main entry point - maintains interactive mode from original."""
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())
    TIDAL_API.apiKey = apiKey.getItem(
        SETTINGS.apiKeyIndex
    )

    if len(sys.argv) > 1:
        mainCommand()
        return

    # Interactive mode
    Printf.logo()
    Printf.settings()

    if not apiKey.isItemValid(
        SETTINGS.apiKeyIndex
    ):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()

    Printf.checkVersion()

    while True:
        Printf.choices()
        from tidal_dl.lang.language import (
            LANG,
        )

        choice = Printf.enter(
            LANG.select.PRINT_ENTER_CHOICE
        )
        if choice == "0":
            return
        elif choice == "1":
            if not loginByConfig():
                loginByWeb()
        elif choice == "2":
            loginByWeb()
        elif choice == "3":
            loginByAccessToken()
        elif choice == "4":
            changePathSettings()
        elif choice == "5":
            changeQualitySettings()
        elif choice == "6":
            changeSettings()
        elif choice == "7":
            if changeApiKey():
                loginByWeb()
        else:
            start(choice)


if __name__ == "__main__":
    main()
else:
    # Only import TIDAL_API when this module is imported as a library
    # This avoids side effects when running as a script
    from tidal_dl.tidal import TIDAL_API
    __all__ = ["TIDAL_API"]
