import json
import os
import shutil
import stat
import sys
import zipfile
from multiprocessing import freeze_support
from pathlib import Path
from subprocess import call
from threading import Thread

import cpuinfo
import requests


# working directory will be ~/.waychess
pwd = Path.home() / ".waychess"

try:
    with open(pwd / "stockfish_links.json", 'r') as fin:
        text = fin.read()
except FileNotFoundError:
    r = requests.get(
            "https://raw.githubusercontent.com/r2dev2bb8/"
            "WayChess/master/stockfish_links.json"
        )
    text = r.text



stockfish_info = json.loads(text)

flags = []


def unzip(filepath: str, resultpath: str) -> None:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(resultpath)

# I know this is camel case, pls don't crucify me
def downloadStockfish() -> None:
    stock_ver = which_stockfish()
    platform = sys.platform.replace("32", '')
    link = stockfish_info[platform][stock_ver]["link"]
    print("Installing stockfish from", link)
    call(["curl", "-o", "stockfish.zip", link])
    unzip("stockfish.zip", str(pwd / "engines" / "stockfish"))
    os.remove("stockfish.zip")
    stockfishexecutable = str(findStockfish())
    if sys.platform != "win32":
        os.chmod(stockfishexecutable, stat.S_IEXEC)


def findStockfish() -> Path:
    stock_ver = which_stockfish()
    platform = sys.platform.replace("32", '')
    location = stockfish_info[platform][stock_ver]["file"]
    return (
        pwd / "engines" / "stockfish" / location
    )

def which_stockfish() -> str:
    """
    Returns which stockfish version to use.

    Changing stockfish version only supported on intel.
    When run on AMD, will always return "bmi2".

    :return: "bmi2", "popcnt", or "64bit"
    """
    if "bmi2" in flags:
        return "bmi2"
    elif "popcnt" in flags:
        return "popcnt"
    else:
        return "64bit"


def create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path)
        os.mkdir(path)


def init():
    with open(pwd / "stockfish_links.json", 'w+') as fout:
        print(text, file=fout)
    r = requests.get(
            "https://raw.githubusercontent.com/r2dev2bb8/"
            "WayChess/master/theme.json"
        )

    with open(pwd / "theme.json", 'w+') as fout:
        print(r.text, file=fout)

    os.mkdir(pwd / "data")
    for filename in (
            "default_theme.json", "FiraCode-Bold.ttf",
            "FiraCode-Regular.ttf", "FiraMono-BoldItalic.ttf",
            "FiraMono-RegularItalic.ttf"):
        r = requests.get(
                "https://raw.githubusercontent.com/MyreMylar/"
                f"pygame_gui/main/pygame_gui/data/{filename}"
            )
        with open(pwd / "data" / filename, 'wb+') as fout:
            fout.write(r.content)



def img_download_task(pwd, img):
    with open(pwd / img["path"], "wb+") as fout:
        url = (
            img["html_url"]
            .replace("github", "raw.githubusercontent")
            .replace("blob/", "")
        )
        print("Saving", url, "to", img["path"], flush=True)
        fout.write(requests.get(url).content)


def img_thread_gen(ext="img"):
    """
    Returns a generator of download and save threads for waychess/img/
    """
    url = "https://api.github.com/repos/r2dev2bb8/waychess/contents/{path}"
    data = requests.get(url.format(path=ext)).json()
    create_dir(pwd / ext)
    for img in data:
        if img["type"] == "dir":
            yield from img_thread_gen(img["path"])
        else:
            yield Thread(target=img_download_task, args=(pwd, img))


def download_img():
    download_threads = list(img_thread_gen())

    for thread in download_threads:
        thread.start()

    for thread in download_threads:
        thread.join()


if __name__ == "__main__":
    freeze_support()
    flags[:] = cpuinfo.get_cpu_info()["flags"]
    try:
        create_dir(pwd)
        init()
        downloadStockfish()
        print("Stockfish has been installed at", findStockfish())
        print("Downloading default images")
        download_img()
    except Exception as e:
        print(e)
        input("Enter to continue (Failed installation)")
