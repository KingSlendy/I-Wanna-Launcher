import os, shutil, subprocess

PYTHON_FOLDER = "Python38"
PYTHON_PATH = f"{PYTHON_FOLDER}\\python.exe"
GENERATED_FOLDER = "Generated"

def main():
    print("Welcome to I Wanna Launcher!")
    name = input("What is the name of your fangame?: ")
    username = input("What is your GitHub username?: ")
    releases = input("Wanna use -Releases after the GitHub repository name? (Y/N): ").lower().strip()
    print("Generating launcher...")
    
    name_full = name
    name_dashes = name.replace(" ", "-")
    name_dots = name.replace(" ", ".")
    name_short = "".join([x[0] for x in name.split(" ")])
    releases = releases if releases in ("y", "n") else "y"
    releases = "-Releases" if releases == "y" else ""
    temp_launcher_folder = f"{GENERATED_FOLDER}\\temp-launcher.exe"
    launcher_folder = f"{GENERATED_FOLDER}\\Launcher.exe"
    icon_folder = f"{GENERATED_FOLDER}\\icon.ico"
    icon = ""

    if os.path.exists(icon_folder):
        icon = f"--icon={icon_folder}"

    if os.path.exists(launcher_folder):
        os.remove(launcher_folder)

    with open(f"{PYTHON_FOLDER}\\launcher.py", "r") as file:
        data = file.read()

    data = data.replace("@@USERNAME@@", username)
    data = data.replace("@@NAME_FULL@@", name_full)
    data = data.replace("@@NAME_DASHES@@", name_dashes)
    data = data.replace("@@NAME_DOTS@@", name_dots)
    data = data.replace("@@NAME_SHORT@@", name_short)
    data = data.replace("@@USE_RELEASES@@", releases)

    with open("temp-launcher.py", "w") as file:
        file.write(data)

    # Generates the launcher
    try:
        subprocess.run(f"{PYTHON_PATH} -m PyInstaller -F {icon} temp-launcher.py")
        shutil.copyfile("dist\\temp-launcher.exe", temp_launcher_folder)
        os.rename(temp_launcher_folder, launcher_folder)
        print(f"Launcher generated succesfully on: {launcher_folder}!")
    except Exception as ex:
        print(f"Error occurred during the launcher generation.\n{ex}")

    # Removes all temp files
    try:
        os.remove("temp-launcher.py")
        shutil.rmtree("build")
        os.remove("temp-launcher.spec")
        shutil.rmtree("dist")
    except Exception as ex:
        print(f"Error occurred during the temporary file deletion.\n{ex}")


if __name__ == "__main__":
    main()