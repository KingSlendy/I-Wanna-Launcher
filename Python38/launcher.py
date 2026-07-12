import json, os, requests, subprocess, time
from tqdm import tqdm
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Link
GITHUB_LINK = f"https://api.github.com/repos/@@USERNAME@@"
GITHUB_REPO = f"@@NAME_DASHES@@@@USE_RELEASES@@"
GITHUB_RELEASES = f"{GITHUB_LINK}/{GITHUB_REPO}/releases/latest"

# Names
GAME_NAME = "Game.exe"
ZIP_NAME = "@@NAME_DOTS@@.zip"
TOKEN_NAME = "token.json"

# OS Paths
CURRENT_PATH = os.getcwd()

# File Paths
GAME_PATH = f"{CURRENT_PATH}\\{GAME_NAME}"
ZIP_PATH = f"{CURRENT_PATH}\\{ZIP_NAME}"
TOKEN_PATH = f"{CURRENT_PATH}\\{TOKEN_NAME}"

class DownloadProgressBar(tqdm):
    def update_to(self, b = 1, bsize = 1, tsize = None):
        if tsize is not None:
            self.total = tsize

        self.update(b * bsize - self.n)


def get_version_number(path):
    version = (0, 0, 0, 0)

    if os.path.exists(path):
        try:
            info = GetFileVersionInfo(path, "\\")
            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]
            version = (HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls))
        except:
            version = (-1, -1, -1, -1)
    
    version = ".".join([str(n) for n in version])
    return version


def main():
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    version = get_version_number(GAME_PATH)

    if version == "-1.-1.-1.-1":
        print("Error validating current version.")
        execute()
        return

    print(f"Current version: {version}")
    print("Validating new version...")

    # Reads the token if token.json exists in the directory
    request_token = None

    try:
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "r") as file:
                request_token = json.load(file)["token"]

            if request_token:
                request_token = request_token.strip()
            else:
                request_token = None
    except (OSError, json.JSONDecodeError, TypeError) as ex:
        print(f"Error reading token from {TOKEN_NAME} file.\n{ex}")
        execute()
        return

    # Makes the first request to get the latest version
    try:
        request_headers = {
            "Accept": "application/vnd.github+json"
        }
            
        if request_token is not None:
            request_headers["Authorization"] = f"Bearer {request_token}"

        with requests.get(GITHUB_RELEASES, headers = request_headers) as response:
            response.raise_for_status()
            game_release = response.json()
            new_game_version = game_release["tag_name"]
    except requests.exceptions.HTTPError as ex:
        print(f"An error occurred during the version request process.\n{ex}")
        execute()
        return

    # Game is up-to-date so it doesn't need to download anything
    if new_game_version == version:
        print("Game is up-to-date!")
        execute()
        return

    print(f"Update version found: {new_game_version}!")
    print(f"Downloading new version...")

    # Finds for the latest release ZIP file
    url_game_zip = None

    for asset in game_release["assets"]:
        if asset["name"] == ZIP_NAME:
            url_game_zip = asset["url"]
            break
    else:
        print(f"Could not find {ZIP_NAME} in the latest release.")
        execute()
        return

    # Makes the second request to download the ZIP file
    try:
        request_headers = {
            "Accept": "application/octet-stream"
        }

        if request_token is not None:
            request_headers["Authorization"] = f"Bearer {request_token}"

        with requests.get(url_game_zip, headers = request_headers, stream = True, allow_redirects = True, timeout = 60) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with DownloadProgressBar(total = total_size, unit = "B", unit_scale = True, miniters = 1, desc = "@@NAME_FULL@@") as bar:
                with open(ZIP_PATH, "wb") as zip:
                    for chunk in response.iter_content(chunk_size = 1024 * 256):
                        if chunk:
                            zip.write(chunk)
                            bar.update(len(chunk))
    except requests.exceptions.HTTPError as ex:
        print(f"An error occurred downloading {ZIP_NAME} from the latest release.\n{ex}")
        execute()
        return

    print(f"@@NAME_FULL@@ {new_game_version} downloaded successfully!")
    print(f"Extracting and executing {ZIP_NAME}...")

    extract_execute()


def execute():
    if os.path.exists(GAME_PATH):
        print("Executing @@NAME_FULL@@...")
        time.sleep(1)
        subprocess.Popen(f"start \"\" \"{GAME_PATH}\" -launch", shell = True)
        time.sleep(0.5)
    else:
        time.sleep(1)


def extract_execute():
    try:
        subprocess.Popen(f"cscript //nologo \"unzip.vbs\" \"{ZIP_PATH}\" \"{CURRENT_PATH}\" && del \"{ZIP_PATH}\" && start \"\" \"{GAME_PATH}\" -launch", shell = True)
    except:
        print(f"Couldn't extract {ZIP_NAME} file, please extract it manually.")
        time.sleep(0.5)


if __name__ == "__main__":
    main()