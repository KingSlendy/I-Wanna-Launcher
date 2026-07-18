import subprocess, sys, time, zipfile
from pathlib import Path

# Files
TRACE_NAME = "trace.txt"

def write_log(message: str) -> None:
    log_path = Path.cwd() / TRACE_NAME

    with log_path.open("a", encoding = "utf-8") as file:
        file.write(f"{message}\n")
        file.flush()

    print(message)


def extract_update(zip_path: Path, destination_path: Path) -> None:
    updater_path = Path(sys.executable).resolve()

    with zipfile.ZipFile(zip_path, "r") as zip:
        for member in zip.infolist():
            target_path = (destination_path / member.filename).resolve()

            if target_path == updater_path:
                print(f"Skipping running extractor: {member.filename}")
                continue

            zip.extract(member, destination_path)


def main() -> None:
    if len(sys.argv) != 3:
        write_log("Usage: updater.exe game.zip launcher.exe")
        raise SystemExit(1)

    zip_path = Path(sys.argv[1]).resolve()
    launcher_path = Path(sys.argv[2]).resolve()

    if not zip_path.is_file():
        write_log(f"ZIP file does not exist: {zip_path}")
        raise SystemExit(1)

    try:
        launcher_path.parent.mkdir(parents = True, exist_ok = True)

        print(f"Extracting {zip_path.name} to: {launcher_path.parent}")

        for _ in range(20):
            try:
                extract_update(zip_path, launcher_path.parent)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            raise OSError(f"ZIP couldn't be extracted.")

        print("ZIP extracted successfully.")

        try:
            print(f"Deleting ZIP: {zip_path}")
            zip_path.unlink()
        except OSError:
            pass

        if not launcher_path.is_file():
            raise FileNotFoundError(f"Launcher does not exist after extraction: {launcher_path}")

        print(f"Restarting launcher: {launcher_path}")

        subprocess.Popen(
            [str(launcher_path), "-launch"],
            cwd = str(launcher_path.parent),
            creationflags = subprocess.CREATE_NO_WINDOW
        )
    except (OSError, zipfile.BadZipFile) as error:
        write_log(f"Failed to install update.\n{error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()