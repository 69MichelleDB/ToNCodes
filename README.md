# ToNCodes

## Intro

Terrors of Nowhere by Beyond is a VRChat horror world where you and other players try to survive different monsters for a period of time. Your progress gets stored as codes that you can copy and paste whenever you want to restore your session. ToNCodes automates the process of storing those codes as they generate within VRChat's logs.

<p align="center">
  <img src="https://github.com/user-attachments/assets/9f856c11-bebd-461a-a68a-c9f0818c743c" />
</p>

This started as a personal application to store all Terrors of Nowhere codes generated while playing, since current available solutions don't work on Linux. I'm not working on it with the intention to replace any existing solutions made for the public, it's mostly an excuse for me to mess with Python and because I believe having multiple choices is always good. You are welcome to use it if you please.

If you find any bugs or want to make suggestions, please open a new issue or let me know on [Discord](https://discord.com/channels/983240485529337856/1340340722011734169).

## IMPORTANT WARNING

This tool is currently in alpha stages and in development, so expect instability and bugs. I'd suggest keeping backups of at least the `Codes` folder where all the xml files are inside the app's folder.

## Notes

> `To run` double click `ToNCodes.bin` (or `ToNCodes.exe` if on Windows).
>
> `Double click` to copy a code.
> 
> `Delete key` to delete a code.
>
> `To update ToNCodes` Unzip the new version and extract the contents inside your app's folder and replace the files. I'd recommend making a backup of the app's folder, just in case you may need to rollback.
>
> If there's a new update ToNCodes will inform you of the new update once and you'll have a reminder on the title bar, this can be disabled in the "File > Options" menu.
>
> `To enable the DEBUG`, in the config.xml file, change the debug-window node value from 0 to 1.
>
> `Manual code insertion`, under "File > Manual code insertion" you can manually add a code if needed.
> 
> `tontrack.me`, you can connect to their Live Tracker by pressing the "Live Tracker" button on the website. Make sure the "File > Options > Connect to tontrack.me" check is enabled (you'll need to restart ToNCodes for the change to take effect if it was disabled).
> 
> `Discord webhook`, you can [create a webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) and add the url to "File > Options > Discord webhook" and any new codes will be send to the Discord channel that webhook was created in.
> 
> `Change language` in File > Options > Language, a restart of ToNCodes is needed for the changes to take effect.

This current version was made under `Python 3.13.02`. If you want to run it, [you can download the latest standalone release](https://github.com/69MichelleDB/ToNCodes/releases/latest) or if you have Python installed, you can clone the project and run `ToNCodes.py`.


## Translations

ToNCodes as of today 2025.04.01 supports multi-language, I'll update this section this week hopefully with instructions of how you can collaborate to help translate.

## Advanced

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
python3 -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --include-package=websockets ToNCodes.py
```

Windows

```powershell
python -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --include-package=websockets --windows-console-mode=disable ToNCodes.py
```

## Credits

**Author:** MichelleDB - https://michelledb.com *I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.*

Terrors of Nowhere belongs to Beyond, https://www.patreon.com/c/beyondVR

Special thanks to Cinnosu for all their support, https://tontrack.me

Thanks MaraRizer and the community for creating and maintaining this neatly organized wiki, https://terror.moe

**Shoutout to the Linux VR Adventures community**: If you're on a Linux distro and want to set up your VR hardware, visit https://lvra.gitlab.io.

Outside dependencies:
[pyperclip](https://github.com/asweigart/pyperclip), [screeninfo](https://github.com/rr-/screeninfo), [cryptography](https://github.com/pyca/cryptography), [requests](https://github.com/psf/requests), [websockets](https://github.com/python-websockets/websockets)
