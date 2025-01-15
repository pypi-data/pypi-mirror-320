from pathlib import Path
import contextlib
import os
from ahk.toggle_icons_c import SRC
import subprocess


@contextlib.contextmanager
def CD(d):
    old = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(old)


CURRENT = Path(__file__).resolve().parent
exe = CURRENT.parent.joinpath("ahk_resources").joinpath("toggle-icons.exe")


def main():
    if not exe.exists():
        CURRENT.joinpath("toggle-icons.c").write_text(SRC, encoding="utf8")
        with CD(str(CURRENT)):
            subprocess.run(
                [
                    "python",
                    "-m",
                    "ziglang",
                    "cc",
                    "toggle-icons.c",
                    "-o",
                    "../ahk_resources/toggle-icons.exe",
                ],
                check=True,
            )
