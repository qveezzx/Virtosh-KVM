#!/usr/bin/bash

# Simple handoff conversion script utilising dmg2img
# Created by qveezzx for Virtosh-KVM

NRS=$1

if [ $NRS = "--nrs" ]
then
./resources/dmg2img ./resources/BaseSystem.dmg
rm ./resources/BaseSystem.dmg
else
./resources/dmg2img ./BaseSystem.dmg
rm ./BaseSystem.dmg
fi


echo 
echo SUCCESS: The BaseSystem file you downloaded was converted and placed into the Virtosh folder for you.
echo