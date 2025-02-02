# ToNCodes

**Current version:** alpha 0.3.0 (2025-02-02)

**Author:** MichelleDB - https://michelledb.com/

*I have no direct relation with Terrors of Nowhere outside of being a fan and a Patreon supporter.*

*Terrors of Nowhere belongs to Beyond https://www.patreon.com/c/beyondVR*

## Intro
This is a personal application to store all Terrors of Nowhere codes generated while playing,the reason I made it is because the current available solutions don't work on linux. 

I'm not making it with the intention to replace any current existing solutions made for the public. This is mostly for personal use and as an excuse to mess with python. You are welcome to use it if you please though.

I'm aware that Beyond may (or may not) be working on a save system using VRC's Persistence, but in the meantime I'd like to be able to easily store my codes while that feature doesn't get added.

## Details
This current version was made under Python 3.10.12. If you want to run it, you can clone the project and run ToNCodes.py

I plan to make the process a bit more straightforward and add it to releases in future versions.

For the clipboard on linux, I'm on Pop!_OS 22.04 on X11 and I needed to download xclip to get it to work
> sudo apt-get install xclip

For wayland sessions you may need xclip, xsel, or wl-clipboard