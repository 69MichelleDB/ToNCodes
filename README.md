# ToNCodes

**Author:** MichelleDB - https://michelledb.com

*I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.*

*[Terrors of Nowhere belongs to Beyond](https://www.patreon.com/c/beyondVR)*

Outside dependencies:
[Pyperclip](https://pypi.org/project/pyperclip/)

## Intro
This is a personal application to store all Terrors of Nowhere codes generated while playing, the reason I made it is because the current available solutions don't work on linux. 

I'm not making it with the intention to replace any current existing solutions made for the public. This is mostly for personal use and as an excuse to mess with python. You are welcome to use it if you please though.

I don't know if Beyond is or isn't working on a save system using VRC's Persistence, but in the meantime I'd like to be able to easily store my codes while that feature doesn't get added.

## Notes
This current version was made under `Python 3.10.12`. If you want to run it [you can download the latest standalone release](https://github.com/69MichelleDB/ToNCodes/releases/latest) or if you have python installed you can clone the project and run `ToNCodes.py`.

**This next section is only if you want to run the python code.**

The project requires `tkinter` and `xclip` (only if you're on linux, xclip is not needed on windows) . On most Linux distributions, you can install it via package manager. 

Debian Ubuntu systems:
```bash
sudo apt-get install python3-tk xclip
```

Red Hat systems:
```bash
sudo dnf install python3-tkinter xclip
```

Arch systems:
```bash
sudo pacman -S tk xclip
```

If `xclip` doesn't work in wayland sessions you may need `xsel` or `wl-clipboard`.


Make sure you also install all the `requirements.txt`

```bash
pip install -r requirements.txt
```

**If you want to compile it into an standalong binary, I used [nuitka](https://nuitka.net/user-documentation/):**. When I compiled it for Windows I used Python 3.12.9, at this moment in time 3.13 is not supported by nuitka.

Debian Ubuntu systems:
```bash
pip install nuitka
```

```bash
python3 -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter ToNCodes.py
```

```powershell
python -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --windows-console-mode=disable ToNCodes.py
```