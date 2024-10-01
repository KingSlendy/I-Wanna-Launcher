import os, re, requests, subprocess, urllib.request, time
from tqdm import tqdm
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Link
GITHUB_LINK = "https://github.com/KingSlendy"
GITHUB_REPO = f"@@NAME_DASHES@@-Releases"

# Names
DATA_NAME = "data.win"
GAME_NAME = "Game.exe"
ZIP_NAME = "@@NAME_SHORT@@.zip"

# OS Paths
CURRENT_PATH = os.getcwd()

# File Paths
DATA_PATH = f"{CURRENT_PATH}\\{DATA_NAME}"
GAME_PATH = f"{CURRENT_PATH}\\{GAME_NAME}"
ZIP_PATH = f"{CURRENT_PATH}\\{ZIP_NAME}"

class DownloadProgressBar(tqdm):
    def update_to(self, b = 1, bsize = 1, tsize = None):
        if tsize is not None:
            self.total = tsize

        self.update(b * bsize - self.n)


def get_version_number(path):
    version = None

    try:
        info = GetFileVersionInfo(path, "\\")
        ms = info["FileVersionMS"]
        ls = info["FileVersionLS"]
        version = (HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls))
    except:
        version = (0, 0, 0, 0)
    
    version = ".".join([str(n) for n in version])
    return version


def main():
    if not os.path.exists(DATA_PATH) or os.path.getsize(DATA_PATH) < 30000000 or not os.path.exists(GAME_PATH):
        print("@@NAME_FULL@@ has not been found, exiting!")
        return

    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    version = get_version_number(GAME_PATH)

    if version == "0.0.0.0":
        print("Error validating current version.")
        execute()
        return
    
    if os.path.exists("test"):
        version += "t"

    print(f"Current version: {version}")
    print("Validating new version...")

    try:
        http_tag_content = requests.get(f"{GITHUB_LINK}/{GITHUB_REPO}/releases/latest").content.decode("utf-8")
        new_game_version = re.search(r"<title>.*(\d+.\d+.\d+.\d+t?).*</title>", http_tag_content)[1]
    except:
        print("An error occurred during the version validation process.")
        execute()
        return

    if new_game_version == version:
        print("Game is up-to-date!")
        execute()
        return

    print(f"Update version found: {new_game_version}!")
    print(f"Downloading new version...")
    url_game_version = f"{GITHUB_LINK}/{GITHUB_REPO}/releases/download/{new_game_version}/@@NAME_DOTS@@.zip"

    try:
        with DownloadProgressBar(unit = 'B', unit_scale = True, miniters = 1, desc = "@@NAME_FULL@@") as bar:
            urllib.request.urlretrieve(url_game_version, filename = ZIP_PATH, reporthook = bar.update_to)
    except:
        print("An error occurred during the downloading update process.")
        execute()
        return

    print("Update downloaded successfully!")
    print("Extracting and executing @@NAME_FULL@@...")

    extract_execute()


def execute():
    print("Executing @@NAME_FULL@@...")
    subprocess.Popen(f"start \"\" \"{GAME_PATH}\" -launch", shell = True)
    time.sleep(0.5)


def extract_execute():
    subprocess.Popen(f"start /B /wait tar -xvf \"{ZIP_PATH}\" && del \"{ZIP_PATH}\" && start \"\" \"{GAME_PATH}\" -launch", shell = True)


if __name__ == "__main__":
    main()