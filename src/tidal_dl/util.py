import os
import shutil


def replace_limit_char(
    path: str, new_char: str
) -> str:
    if path is None:
        return ""
    if new_char is None:
        new_char = ""

    limited_chars = [
        ":",
        "/",
        "?",
        "<",
        ">",
        "|",
        "\\",
        "*",
        '"',
    ]
    for char in limited_chars:
        path = path.replace(
            char, new_char
        )

    path = path.replace("\n", "")
    path = path.replace("\t", "")
    path = path.rstrip(".")
    path = path.strip(" ")
    return path


def mkdirs(path: str) -> bool:
    path = path.replace("\\", "/")
    path = path.strip()
    path = path.rstrip("/")
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            return True
    except:
        return False
    return True
