# ToNCodes

## Intro
<p align="center">
  <img src="https://github.com/user-attachments/assets/f7215a47-92af-4f57-9ccc-85f2b679b152" />
</p>

This started as a personal application to store all Terrors of Nowhere codes generated while playing, the main reason I made it is because the currently available solutions don't work on Linux.

I'm not working on it with the intention to replace any existing solutions made for the public. It's mostly an excuse for me to mess with Python and because I believe having multiple choices is always good. You are welcome to use it if you please.

If you find any bugs or want to make a suggestion, please open a new issue or let me know on [Discord](https://discord.com/channels/983240485529337856/1340340722011734169).

## IMPORTANT WARNING

This tool is currently in alpha stages and in development, so expect instability and bugs. I'd suggest keeping backups of at least the `Codes` folder inside the `ToNCodes folder`.

## Notes

> The Notes field was added on version `alpha-0.5.0`. It's still in development but I hope to have it stable soon as I do more tests.
>
> `To execute` just double click the `ToNCode.bin` (or `ToNCode.exe` if on Windows).
>
> `Double click` to copy a code. `Delete key` to delete a code.
>
> `To update` I'd recommend making a backup of the `ToNCodes folder`, just in case you may need to rollback. Then just unzip the new version, extract the contents inside your `ToNCodes folder` and replace the files.

This current version was made under `Python 3.13.02`. If you want to run it, [you can download the latest standalone release](https://github.com/69MichelleDB/ToNCodes/releases/latest) or if you have Python installed, you can clone the project and run `ToNCodes.py`.

**This next section is only if you want to run the Python code instead of the binary.**

The project requires `tkinter` and `xclip` (only if you're on Linux, xclip is not needed on Windows). On most Linux distributions, you can install it via package manager. 

Debian systems:
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

**If you want to compile it into an standalone binary, you can use [nuitka](https://nuitka.net/user-documentation/)**. When I compiled it for Windows, I used Python 3.12.9. At this moment in time, 3.13 is not supported by it.

```bash
pip install nuitka
```

Linux 

```bash
python3 -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter ToNCodes.py
```

Windows

```powershell
python -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --windows-console-mode=disable ToNCodes.py
```

## Credits

**Author:** MichelleDB - https://michelledb.com

*I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.*

*[Terrors of Nowhere belongs to Beyond](https://www.patreon.com/c/beyondVR)*

*Special thanks to Cinnosu for their support in facilitating the killer data. https://tontrack.me/*

**Big shoutout to the Linux VR Adventures community**: If you're on a Linux distro and want to set up your VR hardware, visit https://lvra.gitlab.io/ for a lot of useful information.

Outside dependencies:
[pyperclip](https://github.com/asweigart/pyperclip), [screeninfo](https://github.com/rr-/screeninfo), [cryptography](https://github.com/pyca/cryptography), [requests](https://github.com/psf/requests)
