#!/usr/bin/env python3
# pylint: disable=C0301,C0116,C0103,R0903

"""
This script was created by Coopydood as part of the ultimate-macOS-KVM project.

https://github.com/user/Coopydood
https://github.com/Coopydood/ultimate-macOS-KVM
Signature: 4CD28348A3DD016F

"""


# COOPYDOOD INTERNAL TERMINAL UI BLUEPRINT


import os
import time
import subprocess
import re 
import json
import sys
import argparse
sys.path.append('./resources/python')
from cpydColours import color

detectChoice = 1
latestOSName = "Tahoe"
latestOSVer = "26"
runs = 0

def clear(): print("\n" * 150)

class cpyd:
    HEADING = "DEBUG TOOLS"
    SUBHEADING = "FOR INTERNAL USE ONLY"

    BODY_1 = "You shouldn't be reading this lol"
    BODY_2 = " "
    BODY_3 = " "
    BODY_4 = " "

    CALLTOACTION = "Available tools:"
    
    USER_SELECT_TITLE_1 = "Reset test environment"
    USER_SELECT_TITLE_2 = "rm AutoPilot blobs"

    USER_SELECT_BODY_1 = "Clean up shit"
    USER_SELECT_BODY_2 = "yeet dem blobs"

    USER_SUBSELECT_TITLE_1 = "Open GitHub page"

    USER_HELP_TITLE = "HELP HEADER"
    USER_ESCAPE_TITLE = "gemme outta here"

    INPUT_FIELD_TEXT = "yeet"




def startup():
    global detectChoice
    print("\n\n  "+color.BOLD+color.GREEN,cpyd.HEADING+color.END,"")
    print("  ",cpyd.SUBHEADING+color.END+"\n")
    print("  ",cpyd.BODY_1,"\n  ",cpyd.BODY_2,"  "+color.END)
    print(color.BOLD+color.RED+"      1.",cpyd.USER_SELECT_TITLE_1)
    print(color.END+color.RED+"        ",cpyd.USER_SELECT_BODY_1+"\n"+color.END)
    print(color.BOLD+"      2.",cpyd.USER_SELECT_TITLE_2)
    print(color.END+"        ",cpyd.USER_SELECT_BODY_2+"\n")
    print(color.END+"      3.",cpyd.USER_SUBSELECT_TITLE_1+"\n")
    print(color.END+"      ?.",cpyd.USER_HELP_TITLE)
    print(color.END+"      Q.",cpyd.USER_ESCAPE_TITLE+"\n")
    detectChoice = str(input(color.BOLD+cpyd.INPUT_FIELD_TEXT+"> "+color.END))

    if detectChoice == "1":
        os.system('./internal/debug-rs.sh')
    elif detectChoice == "2":
        os.system('./internal/rm-blobs.sh')
    elif detectChoice == "3":
        os.system("xdg-open https://github.com/Coopydood/ultimate-macOS-KVM/ > /dev/null 2>&1")
        print("   \nopened the page in ur browser")
    elif detectChoice == "b" or detectChoice == "B":
      os.system('./main.py')
    else:
        clear()
        startup()



def clear(): print("\n" * 150)

startup()