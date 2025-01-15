from ahk.autostart import create
from pathlib import Path
import subprocess
import argparse
import os
from ahk.regenerate import regenerate as init

CURRENT = Path(__file__).resolve().parent
scripts = CURRENT.parent.joinpath("ahk_scripts")


def create_autoruns():
    files = list(scripts.glob("*.ahk"))
    for f in files:
        create(f)


def exec():
    files = list(scripts.glob("*.ahk"))
    for f in files:
        os.startfile(f)


def main():
    if scripts.exists():
        files = scripts.glob("*.ahk")
        for file in files:
            file.unlink()

    init()
    create_autoruns()
    from ahk.toggle_icons import main as main_c

    main_c()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e", "--exec", action="store_true", default=True, help="execute now"
    )

    parser.add_argument(
        "-o", "--open", action="store_true", default=False, help="open startup folder"
    )

    args = parser.parse_args()
    if args.open:
        regjump = CURRENT.parent.joinpath("ahk_resources").joinpath("regjump.exe")
        subprocess.Popen(
            rf"{regjump} HKCU:\Software\Microsoft\Windows\CurrentVersion\Run /accepteula"
        )

    if args.exec:
        exec()


if __name__ == "__main__":
    main()
