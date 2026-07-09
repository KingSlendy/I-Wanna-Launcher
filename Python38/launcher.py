import os, re, requests, subprocess, urllib.request, time
from tqdm import tqdm
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Link
GITHUB_LINK = f"https://api.github.com/repos/@@USERNAME@@"
GITHUB_REPO = f"@@NAME_DASHES@@@@USE_RELEASES@@"
GITHUB_RELEASES = f"{GITHUB_LINK}/{GITHUB_REPO}/releases/latest"

# Names
GAME_NAME = "Game.exe"
ZIP_NAME = "@@NAME_DOTS@@.zip"

# OS Paths
CURRENT_PATH = os.getcwd()

# File Paths
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
    if not os.path.exists(GAME_PATH):
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
        game_release = requests.get(GITHUB_RELEASES).json()
        new_game_version = game_release["tag_name"]
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

    for asset in game_release["assets"]:
        if asset["name"] == ZIP_NAME:
            url_game_zip = asset
            break
    else:
        print(f"Could not find {ZIP_NAME} in the latest release.")
        execute()
        return

    try:
        with DownloadProgressBar(unit = 'B', unit_scale = True, miniters = 1, desc = "@@NAME_FULL@@") as bar:
            urllib.request.urlretrieve(url_game_zip, filename = ZIP_PATH, reporthook = bar.update_to)
    except:
        print(f"An error occurred downloading {ZIP_NAME} from the latest release.")
        execute()
        return

    print(f"@@NAME_FULL@@ {new_game_version} downloaded successfully!")
    print(f"Extracting and executing {ZIP_NAME}...")

    extract_execute()


def execute():
    print("Executing @@NAME_FULL@@...")
    subprocess.Popen(f"start \"\" \"{GAME_PATH}\" -launch", shell = True)
    time.sleep(0.5)


def extract_execute():
    try:
        subprocess.Popen(f"cscript //nologo \"unzip.vbs\" \"{ZIP_PATH}\" \"{CURRENT_PATH}\" && del \"{ZIP_PATH}\" && start \"\" \"{GAME_PATH}\" -launch", shell = True)
    except:
        print("Couldn't extract ZIP file, please extract @@NAME_FULL@@.zip manually.")
        time.sleep(0.5)


if __name__ == "__main__":
    main()