import json, requests, shutil, subprocess, sys, tempfile, time
from pathlib import Path
from tqdm import tqdm
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Link
GITHUB_LINK = f"https://api.github.com/repos/@@USERNAME@@"
GITHUB_REPO = f"@@NAME_DASHES@@@@USE_RELEASES@@"
GITHUB_RELEASES = f"{GITHUB_LINK}/{GITHUB_REPO}/releases/latest"

# Files
ZIP_NAME = "@@NAME_DOTS@@.zip"
TOKEN_NAME = "token.json"
TRACE_NAME = "trace.txt"

class DownloadProgressBar(tqdm):
    def update_to(self, b = 1, bsize = 1, tsize = None) -> None:
        if tsize is not None:
            self.total = tsize

        self.update(b * bsize - self.n)


def write_log(message: str) -> None:
    log_path = Path.cwd() / TRACE_NAME

    with log_path.open("a", encoding = "utf-8") as file:
        file.write(f"{message}\n")
        file.flush()

    print(message)


# Obtains the path of the launcher.exe
def obtain_launcher_path() -> Path:
    launcher_path = Path(sys.executable)
    
    return launcher_path.resolve()


# Obtains the path of the game.exe
def obtain_game_path() -> Path:
    launcher_path = obtain_launcher_path()
    game_path = [path for path in launcher_path.parent.glob("*.exe") if path.resolve() != launcher_path]

    if len(game_path) == 0:
        return None
    
    return game_path[0].resolve()


# Obtains the path of the updater.upt
def obtain_updater_path() -> Path:
    launcher_path = obtain_launcher_path()
    updater_path = [path for path in launcher_path.parent.glob("*.upt")]

    if len(updater_path) == 0:
        return None
    
    return updater_path[0].resolve()


# Obtains the .exe version of the game
def obtain_game_version() -> str:
    game_path = obtain_game_path()
    version = (0, 0, 0, 0)

    if game_path is not None and game_path.is_file():
        try:
            info = GetFileVersionInfo(str(game_path), "\\")
            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]
            version = (HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls))
        except:
            version = (-1, -1, -1, -1)
    
    version = ".".join([str(n) for n in version])
    return version


def game_execute() -> None:
    game_path = obtain_game_path()

    if game_path is not None and game_path.is_file():
        print("Executing @@NAME_FULL@@...")
        time.sleep(1)

        subprocess.Popen(
            [str(game_path), "-launch"],
            cwd = str(game_path.parent),
            creationflags = subprocess.CREATE_NO_WINDOW
        )

        sys.exit()
    else:
        time.sleep(1)


def game_extract(launcher_path: Path, zip_path: Path) -> None:
    try:
        print(f"Extracting and executing @@NAME_FULL@@...")
        time.sleep(1)

        updater_upt_path = obtain_updater_path()
        updater_exe_path = Path(tempfile.gettempdir()) / f"{updater_upt_path.stem}.exe"

        if updater_exe_path.is_file():
            updater_exe_path.unlink()

        shutil.copy2(updater_upt_path, updater_exe_path)

        subprocess.Popen(
            [
                str(updater_exe_path),
                str(zip_path),
                str(launcher_path)
            ],

            cwd = launcher_path.parent,
            creationflags = subprocess.CREATE_NO_WINDOW
        )

        sys.exit()
    except Exception as ex:
        write_log(f"Couldn't extract {ZIP_NAME} file, please extract it manually.\n{ex}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "-launch":
        game_execute()
        return
    
    launcher_path = obtain_launcher_path()

    # Deletes the game.zip file if it exists in the directory
    zip_path = Path(launcher_path.parent) / ZIP_NAME

    if zip_path.is_file():
        zip_path.unlink()

    # Read the game version from the game.exe file
    version = obtain_game_version()

    if version == "-1.-1.-1.-1":
        write_log("Error validating current version.")
        game_execute()
        return

    print(f"Current version: {version}")
    print("Validating new version...")

    # Reads the token.json file if it exists in the directory
    token_path = Path(launcher_path.parent) / TOKEN_NAME
    request_token = None

    try:
        if token_path.is_file():
            with token_path.open("r") as file:
                request_token = json.load(file)["token"]

            if request_token:
                request_token = request_token.strip()
            else:
                request_token = None
    except (OSError, json.JSONDecodeError, TypeError) as ex:
        write_log(f"Error reading token from {TOKEN_NAME} file.\n{ex}")
        game_execute()
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
        write_log(f"An error occurred during the version request process.\n{ex}")
        game_execute()
        return

    # Game is up-to-date so it doesn't need to download anything
    if new_game_version == version:
        print("Game is up-to-date!")
        game_execute()
        return

    print(f"Update version found: {new_game_version}!")
    print(f"Downloading new version...")

    # Finds the latest release ZIP file
    url_game_zip = None

    for asset in game_release["assets"]:
        if asset["name"] == ZIP_NAME:
            url_game_zip = asset["url"]
            break
    else:
        write_log(f"Could not find {ZIP_NAME} in the latest release.")
        game_execute()
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

            with DownloadProgressBar(total = total_size, unit = "B", unit_scale = True, miniters = 1, desc = f"@@NAME_FULL@@ {new_game_version}") as bar:
                with zip_path.open("wb") as zip:
                    for chunk in response.iter_content(chunk_size = 1024 * 256):
                        if chunk:
                            zip.write(chunk)
                            bar.update(len(chunk))
    except requests.exceptions.HTTPError as ex:
        write_log(f"An error occurred downloading {ZIP_NAME} from the latest release.\n{ex}")
        game_execute()
        return

    print(f"@@NAME_FULL@@ {new_game_version} downloaded successfully!")
    game_extract(launcher_path, zip_path)


if __name__ == "__main__":
    main()