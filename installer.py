import os
import stat
import sys
import zipfile
from multiprocessing import freeze_support
from pathlib import Path
from subprocess import call
from threading import Thread

import cpuinfo
import requests


STOCKFISH_DOWNLOAD = {
    "win32": "https://stockfishchess.org/files/stockfish-11-win.zip",
    "linux": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "linux32": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "darwin": "https://stockfishchess.org/files/stockfish-11-mac.zip"
}

STOCKFISH_LOCATION = {
    "win32": r"stockfish\stockfish-11-win\Windows\stockfish_20011801_x64{}.exe",
    "linux": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "linux32": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "darwin": "stockfish/stockfish-11-mac/Mac/stockfish-11-{}"
}


# working directory will be ~/.waychess
pwd = Path.home() / ".waychess" 


def unzip(filepath: str, resultpath: str) -> None:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(resultpath)



# I know this is camel case, pls don't crucify me
def downloadStockfish() -> None:
    link = STOCKFISH_DOWNLOAD[sys.platform]
    print("Installing stockfish from", link)
    call(["curl", "-o", "stockfish.zip", link])
    unzip("stockfish.zip", pwd / "engines"/ "stockfish")
    os.remove("stockfish.zip")
    stockfishexecutable = str(findStockfish())
    if sys.platform != "win32":
        os.chmod(stockfishexecutable, stat.S_IEXEC)



def findStockfish() -> Path:
    toadd = "_bmi2" if sys.platform != "darwin" else "bmi2"
    info = cpuinfo.get_cpu_info()["brand"]
    if '-2' in info:
        toadd = ''
    if '-3' in info:
        toadd = "_modern" if sys.platform != "darwin" else "modern"
    return pwd / "engines" / (STOCKFISH_LOCATION[sys.platform]).format(toadd)


def create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        return


def img_download_task(pwd, img):
    with open(pwd / img["path"], 'wb+') as fout:
        url = img["html_url"] \
                .replace("github", "raw.githubusercontent") \
                .replace("blob/", '')
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
    try:
        create_dir(pwd)
        downloadStockfish()
        print("Stockfish has been installed at", findStockfish())
        print("Downloading default images")
        download_img()
    except Exception as e:
        print(e)
        input("Enter to continue (Failed installation)")

