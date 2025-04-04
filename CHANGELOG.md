# Changelog

## [alpha-0.7.4]

**New**
- First pass for themes. [#38](https://github.com/69MichelleDB/ToNCodes/issues/38)
- Added option to enable debug in File > Options.

**Changes**
- Removed Debug window and integrated it to the bottom of the main window reducing clutter. [#47](https://github.com/69MichelleDB/ToNCodes/issues/47)

**Fixes**
- Checking for updates when you were on the latest version, wasn't displaying the correct message.
- String fixes to ease the translation process at Crowdin.
- Moved Spanish translation to Crowdin.
- Added the message sent by to the Discord webhook when a new code is generated to the locale files. [#40](https://github.com/69MichelleDB/ToNCodes/issues/40)

## [alpha-0.7.3] - 2025.04.01

**New**
- Multi-language support for the UI added. Instructions of how you can contribute, soon. [#31](https://github.com/69MichelleDB/ToNCodes/issues/31)
- English and Spanish added to Options window.

**Changes**
- Changed how Notes are shown in the UI to "Round" round in "Map": "Terrors"
- The window grew horizontally a few pixels.

## [alpha-0.7.2] - 2025.03.31

**New**
- Added a combobox under the horizontal menu where you can filter per VRC log file, reducing the clutter. [#37](https://github.com/69MichelleDB/ToNCodes/issues/37)

**Changes**
- Changed how Notes are shown in the UI to "Round" in "Map": "Terrors"
- Removed the Map ID in the UI.
- GIGABYTES round now labeled as Special instead of Gigabytes.
- Separated UI refresh delay and Log files checking delay.
- Moved the File's name to a combobox, removed the field from the tree view.
- Main window lost some weight and is now smaller

**Fixes**
- 8 pages now show up correctly.
- Fixed bug that would halt UI refreshes if a new code is being written and the UI tries to refresh at the same time.
- Fixed bug where the date would have the word "Debug" after it.
- Optimized Log parsing.

## [alpha-0.7.1] - 2025.03.30


**Changes**
- Reworked how logs are read so it's easier to maintain and expand.
- The rework allowed for full tontrack.me support, thanks a ton Cinossu for the help.
- Added some April fools variants and the special round.

## [alpha-0.6.0]

**New**
- tontrack.me websocket integration, first pass [#36](https://github.com/69MichelleDB/ToNCodes/issues/36) [#33](https://github.com/69MichelleDB/ToNCodes/issues/33)
- Added websockets library to About window.

## [alpha-0.5.5] - 2025.03.21

**New**
- Manual code insertion under `File menu`. [#32](https://github.com/69MichelleDB/ToNCodes/issues/32)

## [alpha-0.5.4] - 2025.03.20

**New**
- Added Unbound data. [#20](https://github.com/69MichelleDB/ToNCodes/issues/20)
- Added cryptography and requests to About window.
- Added debug window, to enable it change the debug-window node in the config.xml file to 1. [#26](https://github.com/69MichelleDB/ToNCodes/issues/26)

**Fixes**
- In case the `control file` gets corrupted or lost, it'll be deleted and a fresh one will be created. Next, ToNCodes will read all available Log files to first find and insert any missing codes and second to regenerate the `control file` with the missing cursor and dates data. [#21](https://github.com/69MichelleDB/ToNCodes/issues/21)
- If the `config file` gets corrupted, it'll be deleted and a new one will be created, prompting the user to review the options. [#29](https://github.com/69MichelleDB/ToNCodes/issues/29)
- If a `code xml file` gets corrupted, it'll be deleted, a new one will be created and it'll scan for codes again. [#28](https://github.com/69MichelleDB/ToNCodes/issues/28)
- Detect if the player didn't join the round. [#22](https://github.com/69MichelleDB/ToNCodes/issues/22)
- Type Fog, Fog (Alternate) and Ghost (Alternate) rounds now detected. [#23](https://github.com/69MichelleDB/ToNCodes/issues/23)
- Getting killed while holding Maxwell doesn't count as losing the round. [#24](https://github.com/69MichelleDB/ToNCodes/issues/24)
- Double Trouble rounds now return which killer is powered up. [#25](https://github.com/69MichelleDB/ToNCodes/issues/25)
- Midnight rounds were not showing the correct alternate.


## [alpha-0.5.3] - 2025.02.25

**Fixes**
- Event detection compatibility with older code xmls.

## [alpha-0.5.2] - 2025.02.25

**New**
- Added Neo Pilot, it gets detected during Winterfest. [#19](https://github.com/69MichelleDB/ToNCodes/issues/19)

**Fixes**
- Alternates were not showing the correct name. [#19](https://github.com/69MichelleDB/ToNCodes/issues/19)

## [alpha-0.5.1] - 2025.02.25

**Fixes**
- Fixed Note decoding to include the case of files created before version `alpha-0.5.0`.
- Fixed os path for the killer data.

## [alpha-0.5.0] - 2025.02.25

**New**
- New entry in the options window to configure the delay between each time ToNCodes checks VRChat's logs files for new codes. [#12](https://github.com/69MichelleDB/ToNCodes/issues/12)
- Redid the logic to parse VRC logs and now we can finally feed the `Notes` field with raw data. [#16](https://github.com/69MichelleDB/ToNCodes/issues/16)
- First draft of the Notes logic added [#3](https://github.com/69MichelleDB/ToNCodes/issues/3)
    - Special thanks to Cinnosu for their support facilitating the killer data~

**Changes**
- Optimizations reading log files. The old algorythm would read a modified file from start to finish every single time, I changed it so in control.xml the file's path, the modification date and the cursor's last position gets stored. That way, if we need to check the log file, we can start from the last position and on boot, we don't need to check all files again. [#8](https://github.com/69MichelleDB/ToNCodes/issues/8) [#13](https://github.com/69MichelleDB/ToNCodes/issues/13)
- About page updated.
- Option window's size changed.
- Option window's webhook text field expanded.
- Webhook also sends note's details.
- Notes in webhook have the same format as in the gui. [#3](https://github.com/69MichelleDB/ToNCodes/issues/3)
- Removed gui-delay entry from config file.
- Changed column sizes.

**Fixes**
- Fixed main window's title.
- Fixed sorting files issue. [#14](https://github.com/69MichelleDB/ToNCodes/issues/14)
- Future proofing in case a new update adds fields to config.xml, add them. [#15](https://github.com/69MichelleDB/ToNCodes/issues/15)
- Fixed small typo on README (thanks eltociear [#17](https://github.com/69MichelleDB/ToNCodes/pull/17))

## [alpha-0.4.0] - 2025.02.14

**New**
- Added discord webhook integration, fill up the text box with the webhook and whenever there's a new code, it'd be sent through that webhook. To stop using it, empty that text box. [#2](https://github.com/69MichelleDB/ToNCodes/issues/2)
- Added Temp folder to store the txt files containing the ToN code before being sent to discord via webhook. These files get cleaned up on boot. [#2](https://github.com/69MichelleDB/ToNCodes/issues/2)
- Added info to the About menu. [#9](https://github.com/69MichelleDB/ToNCodes/issues/9)
- Added the ability to automatically check for new updates on github [#11](https://github.com/69MichelleDB/ToNCodes/issues/11)
- Added new menu point in Options window to select if you ToNCodes to check for updates when the program starts. [#11](https://github.com/69MichelleDB/ToNCodes/issues/11)
- Added new menu point in Files to force check if there's new updates. [#11](https://github.com/69MichelleDB/ToNCodes/issues/11)

**Changes**
- Removed "//// [Double click to copy]" from the window's title.
- Added dependencies information.
- Minor optimizations when handling xml files.
- Changed how the gui is organized for the configuration window, from pack to grid.
- `About` no longer is a cascade menu but a single item.  [#9](https://github.com/69MichelleDB/ToNCodes/issues/9)
- Better error handling and logging. [#6](https://github.com/69MichelleDB/ToNCodes/issues/6)

**Fixes**
- Options > Saving doesn't close the window. Fixes [#5](https://github.com/69MichelleDB/ToNCodes/issues/5)
- Fixed a bug where on first boot it would start checking for logs before VRC's path is saved in the `config.xml` file
- Fixed a bug where the temporal webhook files would be created with forbidden characters [#10](https://github.com/69MichelleDB/ToNCodes/issues/10)

## [alpha 0.3.6] - 2025.02.11

**New**
- Automatically finds ToN codes in VRChat's logs and saves them in .xml files inside the Codes folder.
- You can copy a selected Code in the list by double clicking.
- You can delete a selected Code by pressing the "Delete" key on your keyboard.