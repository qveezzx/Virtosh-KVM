#!/usr/bin/env python3
# pylint: disable=C0301,C0116,C0103,R0903

"""

Signature: n/a

"""
import os
import time
import subprocess
import re 
import json
import sys
import argparse
sys.path.append('./resources/python')
from cpydColours import color

output_stream = os.popen('lspci -k | grep -B 2 "vfio-pci"')
vgaGrep = output_stream.read()

vfioCount = vgaGrep.count("vfio-pci")

print("\n")
if vfioCount >= 2:
    print("I"+color.BOLD+color.GREEN,"successfully"+color.END,"detected"+color.BOLD,vfioCount,"devices correctly bound to vfio-pci"+color.END,"in your system.\n")
elif vfioCount == 1:
    print("I"+color.BOLD+color.GREEN,"successfully"+color.END,"detected"+color.BOLD,vfioCount,"device correctly bound to vfio-pci"+color.END,"in your system.\n")
else:
    print("I"+color.BOLD+color.RED,"failed"+color.END,"to detect any devices correctly bound to vfio-pci in your system.\nYou must make sure your"+color.BOLD,"vfio-ids"+color.END,"are entered in your host boot-args.\n")
print("\n",vgaGrep)

print(color.BOLD+color.CYAN+"HOW TO:"+color.END,"For each device you intend on passing through, you must \"stub\" it\n        to the"+color.BOLD+" vfio-pci kernel driver."+color.END+" This is done by modifying your "+color.BOLD+"\n        mkinitcpio.conf and boot-args. "+color.END+"See GitHub for instructions!")
print("\n"+color.BOLD+"         Example:"+color.END,"...loglevel=3 intel_iommu=1..."+color.BOLD+color.YELLOW+color.UNDERLINE+"vfio-pci.ids=1002:67ff,1002:aae0"+color.END+"\n")