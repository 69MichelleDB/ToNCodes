#!/bin/bash

# Make sure the folder that stores the builds exists
binaryFolder="BuildBin"
if [ ! -d "$binaryFolder" ]; then
    mkdir "$binaryFolder"
fi

finalFolder="ToNCodes"

# Read the _VERSION value from Globals.py
_VERSION=$(grep -m1 "_VERSION" Globals.py | awk -F "=" '{print $2}' | tr -d " '\n")

zipFile=ToNCodes-linux-${_VERSION}.zip

# Copy the project, I don't want to clog the original with junk from the compilation
folder=$(basename $(pwd))
folderCopy=${folder}_compcopy
cd ${binaryFolder}
cp -r ../../$folder ../../${folderCopy}
mv ../../${folderCopy} ./

# Go in and compile
cd ./${folderCopy}
python3 -m nuitka --standalone --follow-imports --onefile --enable-plugin=tk-inter --include-package=websockets --assume-yes-for-downloads ToNCodes.py

# Create structure and clean up
mkdir "$finalFolder"
mv ToNCodes.bin ${finalFolder}
mv Templates ${finalFolder}
mv CHANGELOG.md ${finalFolder}
mv LICENSE.txt ${finalFolder}
mv README.md ${finalFolder}
mkdir ${finalFolder}/Codes
mkdir ${finalFolder}/Logs
mkdir ${finalFolder}/Temp
mkdir ${finalFolder}/Tools
mkdir ${finalFolder}/Tools/Items
mkdir ${finalFolder}/Tools/Locale
mkdir ${finalFolder}/Tools/Themes
mkdir ${finalFolder}/Tools/OSC
mv Tools/Items/silly.json ${finalFolder}/Tools/Items
mv Tools/Locale ${finalFolder}/Tools
mv Tools/Themes/*.json ${finalFolder}/Tools/Themes
rm ${finalFolder}/Tools/Themes/*-test.json
mv ${finalFolder} ../

cd ..
rm -rf ./${folderCopy}

zip -r ${zipFile} ${finalFolder}
sha256sum ${zipFile} > sha256linux.txt

rm -rf ./${finalFolder}