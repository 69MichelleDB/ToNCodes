# Changelog

## [WIP] - 2025..

### New
- Added discord webhook integration, fill up the text box with the webhook and whenever there's a new code, it'd be sent through that webhook. To stop using it, empty that text box. [#2](https://github.com/69MichelleDB/ToNCodes/issues/2)
- Added Temp folder to store the txt files containing the ToN code before being sent to discord via webhook. These files get cleaned up on boot.
- Added info to the About menu.

### Changes
- Removed "//// [Double click to copy]" from the window's title.
- Added dependencies information.
- Minor optimizations when handling xml files.
- Changed how the gui is organized for the configuration window, from pack to grid.
- About no longer is a cascade menu but a single item.

### Fixes
- Options > Saving doesn't close the window. Fixes [#5](https://github.com/69MichelleDB/ToNCodes/issues/5)
- Fixed a bug where on first boot it would start checking for logs before VRC's path is saved in the `config.xml` file
- Fixed a bug where the temporal webhook files would be created with forbidden characters [#10](https://github.com/69MichelleDB/ToNCodes/issues/10)

## [alpha 0.3.6] - 2025.02.11

### New
- Automatically finds ToN codes in VRChat's logs and saves them in .xml files inside the Codes folder.
- You can copy a selected Code in the list by double clicking.
- You can delete a selected Code by pressing the "Delete" key on your keyboard.

