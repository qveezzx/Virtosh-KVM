#!/bin/bash

# Download and install Barrier seamlessly for use with VIRTOSH
# Created by qveezzx for Virtosh-KVM

echo "###############################################"
echo "WELCOME TO THE Virtosh BARRIER INSTALLER"
echo "###############################################"
echo "" 
echo "This script will download, install, and"
echo "configure the Barrier application for use"
echo "with the Virtosh project."
echo ""
echo "Press ENTER to continue."
read -p ""
clear
echo "###############################################"
echo "DOWNLOADING..."
echo "###############################################"
echo "" 
echo "Please wait..."
echo ""
mkdir ~/Virtosh
cd ~/Virtosh
curl -L -O https://github.com/debauchee/barrier/releases/download/v2.4.0/Barrier-2.4.0-release.dmg
# wget -q https://raw.githubusercontent.com/qveezzx/Virtosh-KVM/main/resources/com.github.Barrier.plist
clear
echo "###############################################"
echo "INSTALLING..."
echo "###############################################"
echo "" 
echo "Please wait..."
echo ""
hdiutil mount Barrier-2.4.0-release.dmg
sleep 5
cp -R /Volumes/Barrier/Barrier.app /Applications/Barrier.app
cp com.github.Barrier.plist ~/Library/Preferences/com.github.Barrier.plist
hdiutil unmount /Volumes/Barrier
clear
echo "###############################################"
echo "DONE"
echo "###############################################"
echo "" 
echo "Launching..."
echo ""
open -a Barrier.app
