import os, shutil, subprocess

def main():
    print("Welcome to I Wanna Launcher!")
    name = input("What is the name of your fangame?: ")
    print("Generating launcher...")
    
    name_full = name
    name_dashes = name.replace(" ", "-")
    name_dots = name.replace(" ", ".")
    name_short = "".join([x[0] for x in name.split(" ")])

    with open("launcher.py", "r") as file:
        data = file.read()

    data = data.replace("@@NAME_FULL@@", name_full)
    data = data.replace("@@NAME_DASHES@@", name_dashes)
    data = data.replace("@@NAME_DOTS@@", name_dots)
    data = data.replace("@@NAME_SHORT@@", name_short)

    with open("temp-launcher.py", "w") as file:
        file.write(data)

    libraries = ["requests", "tqdm", "pywin32", "pyinstaller"]

    for library in libraries:
        subprocess.run(f"pip install {library}")

    subprocess.run(f"pyinstaller -F temp-launcher.py")
    os.remove("temp-launcher.py")
    shutil.rmtree("build")
    os.remove("temp-launcher.spec")
    shutil.copyfile("dist\\temp-launcher.exe", "temp-launcher.exe")
    os.rename("temp-launcher.exe", f"{name_full}.exe")
    shutil.rmtree("dist")

    
if __name__ == "__main__":
    main()