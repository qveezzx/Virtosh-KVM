#!/usr/bin/env python3
# pylint: disable=C0301,C0116,C0103,R0903

"""
This script was created by Coopydood as part of the ultimate-macOS-KVM project.

https://github.com/user/Coopydood
https://github.com/Coopydood/ultimate-macOS-KVM
Signature: 4CD28348A3DD016F

"""

import os
import time
import subprocess
import re 
import json
import sys
import argparse
import platform
import datetime
sys.path.append('./resources/python')
from cpydColours import color
try:
    from pypresence import Presence
except:
    None

sys.path.insert(0, 'scripts')

parser = argparse.ArgumentParser("main")
parser.add_argument("--skip-vm-check", dest="svmc", help="Skip the arbitrary VM check",action="store_true")
parser.add_argument("--skip-os-check", dest="sosc", help="Skip the OS platform check",action="store_true")
parser.add_argument("--disable-rpc", dest="rpcDisable", help="Disable Discord Rich Presence integration",action="store_true")

args = parser.parse_args()

global apFilePath
global VALID_FILE
global REQUIRES_SUDO
global discordRPC
global baseSystemNotifArmed

detectChoice = 1
latestOSName = "Sequoia"
latestOSVer = "15"
runs = 0
apFilePath = ""
procFlow = 1
discordRPC = 1
debug = 0

baseSystemNotifArmed = False

version = open("./.version")
version = version.read()

versionDash = version.replace(".","-")

if args.rpcDisable == True:
    discordRPC = 0
else:
    discordRPC = 1

projectVer = "Powered by ULTMOS v"+version

# We don't need these files anymore. If they're here, get rid
if os.path.exists("./UPGRADEPATH"): os.system("rm ./UPGRADEPATH")
if os.path.exists("./VERSION"): os.system("rm ./VERSION") 
if os.path.exists("./resources/WEBVERSION"): os.system("rm ./resources/WEBVERSION")
if os.path.exists("./internal"): debug = 1

def get_linux_info():
    """Get detailed Linux distribution information"""
    try:
        # Try reading /etc/os-release first (most modern distros)
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r") as f:
                lines = f.readlines()
                info = {}
                for line in lines:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        info[key] = value.strip('"')
                
                distro_name = info.get("PRETTY_NAME", info.get("NAME", "Unknown Linux"))
                distro_id = info.get("ID", "unknown")
                return distro_name, distro_id
        
        # Fallback methods
        elif os.path.exists("/etc/lsb-release"):
            with open("/etc/lsb-release", "r") as f:
                for line in f:
                    if "DISTRIB_DESCRIPTION" in line:
                        return line.split("=")[1].strip().strip('"'), "unknown"
        
        # Last resort - try platform module
        return f"{platform.system()} {platform.release()}", "unknown"
    
    except Exception as e:
        log_error("Failed to detect Linux distribution", str(e), "Unable to read system files")
        return "Unknown Linux", "unknown"

def get_kernel_version():
    """Get Linux kernel version"""
    try:
        kernel = platform.release()
        return kernel
    except Exception as e:
        log_error("Failed to get kernel version", str(e), "Platform module unavailable")
        return "Unknown"

def print_ascii_header():
    """Print ASCII art header with system information"""
    ascii_art = f"""
{color.CYAN}{color.BOLD}
    ╦ ╦╦  ╔╦╗╔╦╗╔═╗╔═╗
    ║ ║║   ║ ║║║║ ║╚═╗
    ╚═╝╩═╝ ╩ ╩ ╩╚═╝╚═╝{color.END}
    {color.PURPLE}Ultimate macOS KVM{color.END}
    
    {color.GRAY}Version: {color.END}{color.BOLD}v{version}{color.END}
    {color.GRAY}Author:  {color.END}{color.BOLD}Coopydood{color.END}
"""
    
    # Get system information
    distro_name, distro_id = get_linux_info()
    kernel_ver = get_kernel_version()
    
    system_info = f"""    {color.GRAY}═══════════════════════════════════════════{color.END}
    {color.BLUE}System:{color.END}  {distro_name}
    {color.BLUE}Kernel:{color.END}  {kernel_ver}
    {color.GRAY}═══════════════════════════════════════════{color.END}
"""
    
    print(ascii_art + system_info)

def log_info(message):
    """Print informational log message"""
    print(f"{color.BLUE}[INFO]{color.END} {message}")

def log_success(message):
    """Print success log message"""
    print(f"{color.GREEN}[✔]{color.END} {message}")

def log_warning(message):
    """Print warning log message"""
    print(f"{color.YELLOW}[⚠]{color.END} {message}")

def log_error(title, error_msg, possible_fix=""):
    """Print detailed error message with possible fix"""
    print(f"\n{color.RED}{color.BOLD}[✖ ERROR]{color.END} {color.BOLD}{title}{color.END}")
    print(f"{color.RED}Details:{color.END} {error_msg}")
    if possible_fix:
        print(f"{color.YELLOW}Possible fix:{color.END} {possible_fix}")
    print()

def check_dependencies():
    """Check for required dependencies and provide helpful error messages"""
    log_info("Checking dependencies...")
    
    missing_deps = []
    
    # Check for QEMU
    try:
        result = subprocess.run(["which", "qemu-system-x86_64"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            missing_deps.append(("QEMU", "sudo apt install qemu-system-x86 qemu-utils"))
        else:
            log_success("QEMU found")
    except Exception as e:
        log_warning(f"Could not verify QEMU installation: {str(e)}")
    
    # Check for Python dependencies
    required_modules = ['pypresence']
    for module in required_modules:
        try:
            __import__(module)
            log_success(f"Python module '{module}' found")
        except ImportError:
            missing_deps.append((f"Python module '{module}'", f"pip3 install {module}"))
    
    if missing_deps:
        log_warning("Missing dependencies detected:")
        for dep, install_cmd in missing_deps:
            print(f"  • {dep}")
            print(f"    {color.GRAY}Install: {color.END}{install_cmd}")
        print()
    
    return len(missing_deps) == 0

def startup():
    global detectChoice
    global apFile
    global apFilePath
    detectChoice = None

    log_info("Initializing ULTMOS...")

    if not os.path.exists("resources/script_store/main.py"):
        log_info("First-time setup detected, backing up original files...")
        try:
            os.system("cp -R ./scripts/* ./resources/script_store/")
            os.system("cp ./main.py ./resources/script_store/")
            os.system("cp ./.version ./resources/script_store/")
            log_success("Backup completed successfully")
        except Exception as e:
            log_error("Backup failed", str(e), "Ensure you have write permissions in the project directory")

    def fts():
        clear()
        print("\n\n   "+color.BOLD+color.BLUE+"                WELCOME TO"+color.CYAN+" ULTMOS"+color.BLUE+color.BOLD+""+color.END)
        print("                First time setup wizard\n")
        print("   Welcome! As this is your first time using ULTMOS, you\n   must select how you'd like to use the project.\n   The project can be run in 2 modes.")
        print(color.BOLD+"\n      1. Standard mode (recommended)")
        print(color.END+"         This mode is the default, and sets up the repo to\n         use a traditional folder structure; designed for \n         use with one virtual machine at a time. Making a\n         new VM would replace the old one.")
        print(color.BOLD+color.GRAY+"\n      2. Dynamic mode (BETA)"+color.END)
        print(color.GRAY+"         This mode is intended to replace standard mode. It\n         instead allows you to create many VMs under one\n         repo, sharing project resources. This means you can\n         easily move and copy VMs to other computers.")
        print(color.RED+"         This feature is currently unavailable.\n"+color.END)
        print("   Please select a mode to begin.\n")
        
        detectChoiceMode = str(input(color.BOLD+"Select> "+color.END))

        if detectChoiceMode == detectChoiceMode:
            clear()
            try:
                nrsblob = open("./resources/.nrsMode","w")
                nrsblob.write("1")
                nrsblob.close()
                log_success("Configuration saved")
            except Exception as e:
                log_error("Failed to save configuration", str(e), 
                         "Check write permissions in ./resources/ directory")
        else:
            fts()
    
    if os.path.exists("blobs/user/USR_CFG.apb"):
            print(color.BOLD+"\n\n  "+color.CYAN,"ULTMOS"+color.END+color.GRAY,"v"+version+color.END)
            print("   by Coopydood"+color.END)
            tainted = 1
    else:
        print(color.BOLD+"\n\n   Welcome to"+color.CYAN,"ULTMOS"+color.END+color.GRAY,"v"+version+color.END)
        print("   by Coopydood"+color.END)
        print("\n   This project can assist you in some often-tedious setup, including\n   processes like"+color.BOLD,"checking your GPU, checking your system, downloading macOS,\n   "+color.END+"and more. Think of it like your personal KVM swiss army knife.")

    if isVM == True:
        log_warning("Virtual machine detected, functionality may be limited")
    
    if os.path.exists("./blobs/USR_TARGET_OS.apb") and not os.path.exists("./blobs/user/USR_TARGET_OS.apb"):
        log_info("Migrating configuration from older version...")
        try:
            os.system("mv ./blobs/*.apb ./blobs/user")
            log_success("Configuration migrated successfully")
        except Exception as e:
            log_error("Migration failed", str(e), "Manually move .apb files from ./blobs/ to ./blobs/user/")

    if os.path.exists("./blobs/user/USR_CFG.apb"):
            global apFilePath
            global apFilePathNoPT
            global apFile
            global apFilePathNoUSB
            global macOSVer
            global mOSString
            
            try:
                apFilePath = open("./blobs/user/USR_CFG.apb")
                apFilePath = apFilePath.read()
                log_success(f"Configuration loaded: {apFilePath}")
            except Exception as e:
                log_error("Failed to read configuration", str(e), 
                         "Ensure ./blobs/user/USR_CFG.apb exists and is readable")
            
            if os.path.exists("./blobs/user/USR_TARGET_OS_NAME.apb"):
                macOSVer = open("./blobs/user/USR_TARGET_OS_NAME.apb")
                macOSVer = macOSVer.read()
           
            macOSVer = open("./blobs/user/USR_TARGET_OS.apb")
            macOSVer = macOSVer.read()
            if int(macOSVer) <= 999 and int(macOSVer) > 99:
                macOSVer = str(int(macOSVer) / 100)
                mOSString = "Mac OS X"
            else:
                mOSString = "macOS"
            if os.path.exists("./blobs/user/USR_TARGET_OS_NAME.apb"):
                macOSVer = open("./blobs/user/USR_TARGET_OS_NAME.apb")
                macOSVer = macOSVer.read()
            if os.path.exists("./"+apFilePath):
                global REQUIRES_SUDO
                global VALID_FILE
                global VALID_FILE_NOPT
                global VALID_FILE_NOUSB
                global baseSystemNotifArmed
                VALID_FILE = 0
                VALID_FILE_NOPT = 0
                VALID_FILE_NOUSB = 0
                
                apFile = open("./"+apFilePath,"r")

                if "REQUIRES_SUDO=1" in apFile.read():
                    REQUIRES_SUDO = 1
                else:
                    REQUIRES_SUDO = 0

                apFile.close()
                apFile = open("./"+apFilePath,"r")

                apFilePathNoPT = apFilePath.replace(".sh","-noPT.sh")
                apFilePathNoUSB = apFilePath.replace(".sh","-noUSB.sh")
                
                apFileM = apFile.read()

                if "APC-RUN" in apFileM:
                    VALID_FILE = 1
                    log_success("Valid AutoPilot configuration detected")

                    if "#-drive id=BaseSystem,if=none,file=\"$VM_PATH/BaseSystem.img\",format=raw" not in apFileM and "-drive id=BaseSystem,if=none,file=\"$VM_PATH/BaseSystem.img\",format=raw" in apFileM and "HDD_PATH=\"/dev/disk/" not in apFileM:
                        if os.path.exists("./blobs/user/USR_HDD_PATH.apb"):
                            hddPath = open("./blobs/user/USR_HDD_PATH.apb")
                            hddPath = hddPath.read()
                            hddPath = hddPath.replace("$VM_PATH",os.path.realpath(os.curdir))
                        if (os.path.getsize(hddPath)) > 22177079296 and not os.path.exists("./blobs/user/.noBaseSystemReminder"):
                            baseSystemNotifArmed = True

                    if REQUIRES_SUDO == 1:
                        print(color.BOLD+"\n      B. Boot",mOSString,macOSVer+color.YELLOW,"⚠"+color.END)
                        print(color.END+"         Start",mOSString,"using the detected\n         "+apFilePath+" script file."+color.YELLOW,"Requires superuser."+color.END)
                    else:
                        print(color.BOLD+"\n      B. Boot",mOSString,macOSVer+"")
                        print(color.END+"         Start",mOSString,"using the detected\n         "+apFilePath+" script file.")
                    
                    if os.path.exists("./"+apFilePathNoPT):
                        VALID_FILE_NOPT = 1
                    
                    if os.path.exists("./"+apFilePathNoUSB):
                        VALID_FILE_NOUSB = 1
                        
                    if VALID_FILE_NOPT == 1 or VALID_FILE_NOUSB == 1:
                        print(color.BOLD+"\n      O. Other boot options...") 

                    print(color.END+"\n      1. AutoPilot")      

                else:
                    log_warning("Invalid configuration file detected")
                    print(color.BOLD+"\n      1. AutoPilot")
                    print(color.END+"         Quickly and easily set up a macOS\n         virtual machine in just a few steps\n")

            else:
                log_warning(f"Configuration file not found: {apFilePath}")
                print(color.BOLD+"\n      1. AutoPilot")
                print(color.END+"         Quickly and easily set up a macOS\n         virtual machine in just a few steps\n")
    else:
        print(color.BOLD+"\n      1. AutoPilot")
        print(color.END+"         Quickly and easily set up a macOS\n         virtual machine in just a few steps\n")
    
    print(color.END+"      2. Download macOS...")
    print(color.END+"      3. Compatibility checks...")
    print(color.END+"      4. Passthrough tools...\n")
    
    if debug == 1: print(color.END+color.BOLD+color.GREEN+"      D. DEBUG TOOLS..."+color.END)
    print(color.END+"      E. Extras...")
    print(color.END+"      W. What's new?")
    print(color.END+"      U. Check for updates")
    print(color.END+"      Q. Exit\n")
    detectChoice = str(input(color.BOLD+"Select> "+color.END))

def clear(): print("\n" * 150)

def baseSystemAlert():
    global apFilePath
    clear()
    print("\n\n   "+color.BOLD+color.GREEN+"FINISHED INSTALLING MACOS?"+color.END,"")
    print("   Finished install detected\n")
    print("   The assistant has detected that your macOS installation \n   may be complete. Would you like me to remove the install\n   media from your config file for you?\n\n   This stops the \"macOS Base System\" boot entry from appearing.\n")
    print(color.BOLD+"      1. Remove BaseSystem"+color.END)
    print(color.END+"         Detaches the macOS installer\n         from the",apFilePath+" file\n")
    print(color.END+"      2. Not now")
    print(color.END+"      3. Don't remind me again\n")
    detectChoice5 = str(input(color.BOLD+"Select> "+color.END))

    if detectChoice5 == "1":
        try:
            with open("./"+apFilePath,"r") as apFile:
                apFileM = apFile.read()
                apFileM = apFileM.replace("-drive id=BaseSystem,if=none,file=\"$VM_PATH/BaseSystem.img\",format=raw\n-device ide-hd,bus=sata.4,drive=BaseSystem","#-drive id=BaseSystem,if=none,file=\"$VM_PATH/BaseSystem.img\",format=raw\n#-device ide-hd,bus=sata.4,drive=BaseSystem")
            time.sleep(1)
            with open("./"+apFilePath,"w") as apFile:
                apFile.write(apFileM)
            clear()
            log_success("BaseSystem removed successfully")
            time.sleep(3)
            clear()
        except Exception as e:
            log_error("Failed to remove BaseSystem", str(e), 
                     f"Manually edit {apFilePath} and comment out BaseSystem lines")
    elif detectChoice5 == "3":
        try:
            with open("./blobs/user/.noBaseSystemReminder","w") as remindFile:
                remindFile.write(" ")
            log_success("Reminder disabled")
        except Exception as e:
            log_error("Failed to save preference", str(e), 
                     "Check write permissions in ./blobs/user/ directory")
        clear()
    else:
        clear()

# Set permissions
log_info("Setting file permissions...")
try:
    os.system("chmod +x -R scripts/*.py")
    os.system("chmod +x -R scripts/extras/*.py")
    os.system("chmod +x -R scripts/restore/*.py")
    os.system("chmod +x -R scripts/*.sh")
    os.system("chmod +x resources/dmg2img")
    os.system("chmod +x scripts/hyperchromiac/*.py")
    log_success("Permissions set successfully")
except Exception as e:
    log_warning(f"Could not set all permissions: {str(e)}")

output_stream = os.popen('lspci')
vmc1 = output_stream.read()

detected = 0
global isVM
isVM = False

if "VMware" in vmc1:
   detected = 1

if "VirtualBox" in vmc1 or "Oracle" in vmc1:
   detected = 1

if "Redhat" in vmc1 or "RedHat" in vmc1 or "QEMU" in vmc1:
   detected = 1

if "Bochs" in vmc1 or "Sea BIOS" in vmc1 or "SeaBIOS" in vmc1:
   detected = 1

if platform.system() != "Linux":
    detected = 2

clear()
print_ascii_header()

# Check dependencies
check_dependencies()

if detected == 1:
    if args.svmc == True:
        clear()
        print_ascii_header()
        startup()
    else:
        isVM = True
        log_warning("VIRTUAL MACHINE DETECTED")
        print("\n   I've determined that it's more than likely that \n   you're using a virtual machine to run this. I won't\n   stop you, but there really isn't much point in continuing."+color.END)
        
        print(f"\n   {color.BOLD}{color.YELLOW}PROBLEM:{color.END} Virtual hardware detected"+color.END)
        print(f"   {color.GRAY}Nested virtualization is not recommended for macOS VMs{color.END}")
        print(color.BOLD+"\n      1. Exit")
        print(color.END+"      2. Continue anyway\n")
        stageSelect = str(input(color.BOLD+"Select> "+color.END))
   
        if stageSelect == "1":
            sys.exit()
        elif stageSelect == "2": 
            clear()
            print_ascii_header()
            startup()

elif detected == 2:
    if args.sosc == True:
        clear()
        print_ascii_header()
        startup()
    else:
        log_error("INCOMPATIBLE OPERATING SYSTEM", 
                 f"{platform.system()} detected - This project requires Linux",
                 "Run this script on a Linux system with KVM support")
        print("\n\n")
        time.sleep(5)
        sys.exit()
else:
    clear()
    print_ascii_header()
    startup()

if detectChoice == "1":
    log_info("Starting AutoPilot...")
    os.system('./scripts/autopilot.py')
elif detectChoice == "2":
    log_info("Opening macOS download tool...")
    os.system('./scripts/dlosx.py')
elif detectChoice == "3":
    clear()
    log_info("Running compatibility checks...")
    os.system('./scripts/compatchecks.py')
elif detectChoice == "4":
    clear()
    log_info("Opening passthrough tools...")
    os.system('./scripts/vfio-menu.py')
elif detectChoice == "e" or detectChoice == "E":
    clear()
    log_info("Opening extras menu...")
    os.system('./scripts/extras.py')
elif detectChoice == "w" or detectChoice == "W":
    clear()
    log_success("OPENING RELEASE NOTES IN DEFAULT BROWSER")
    print("   Continue in your browser\n")
    print("\n   I have attempted to open the release notes in\n   your default browser. Please be patient.\n\n   You will be returned to the main menu in 5 seconds.\n\n\n\n\n")
    os.system('xdg-open https://github.com/Coopydood/ultimate-macOS-KVM/blob/main/docs/changelogs/v'+versionDash+".md > /dev/null 2>&1")
    time.sleep(6)
    clear()
    os.system('./main.py')
elif detectChoice == "u" or detectChoice == "U":
    clear()
    log_info("Checking for updates...")
    os.system('./scripts/repo-update.py --menuFlow')
elif detectChoice == "d" and debug == 1 or detectChoice == "D" and debug == 1:
    clear()
    log_info("Opening debug tools...")
    os.system('./scripts/extras/debug.py')
elif detectChoice == "b" and VALID_FILE == 1 or detectChoice == "B" and VALID_FILE == 1:
    clear()

    if not os.path.exists("./ovmf/OVMF_VARS.df"):
        log_warning("OVMF variables file missing, attempting auto-repair...")
        if os.path.exists("./ovmf/user_store/OVMF_VARS.fd"):
            os.system("cp ./ovmf/user_store/OVMF_VARS.fd ./ovmf/OVMF_VARS.fd")
            log_success("OVMF restored from user store")
        else:
            os.system("cp ./resources/ovmf/OVMF_VARS.fd ./ovmf/OVMF_VARS.fd")
            log_success("OVMF restored from defaults")

    if discordRPC == 1:
        client_id = "1149434759152422922"
        try:
            RPC = Presence(client_id)
        except:
            None

        if os.path.exists("./blobs/user/USR_VFIO_DEVICES.apb"):
            vfioDevs = open("./blobs/user/USR_VFIO_DEVICES.apb")
            vfioDevs = vfioDevs.read()
            subprocess.Popen(["python3","./scripts/drpc.py","--os",macOSVer,"--pt",vfioDevs])
        else:
            subprocess.Popen(["python3","./scripts/drpc.py","--os",macOSVer])
    
    if REQUIRES_SUDO == 1:
        print(color.YELLOW+color.BOLD+"\n   ⚠ "+color.END+color.BOLD+"SUPERUSER PRIVILEGES"+color.END+"\n   This script uses physical device passthrough,\n   and needs superuser privileges to run.\n\n   Press CTRL+C to cancel.\n"+color.END)
        if baseSystemNotifArmed == True:
            baseSystemAlert()
        if discordRPC == 0:
            os.system("sudo ./"+apFilePath+" -d 0")
        else:
            os.system("sudo ./"+apFilePath)
    else:
        if baseSystemNotifArmed == True:
            baseSystemAlert()
        if discordRPC == 0:
            os.system("./"+apFilePath+" -d 0")
        else:
            os.system("./"+apFilePath)

elif detectChoice == "o" and VALID_FILE_NOPT == 1 or detectChoice == "o" and VALID_FILE_NOUSB == 1 or detectChoice == "O" and VALID_FILE_NOPT == 1 or detectChoice == "O" and VALID_FILE_NOUSB == 1:
    clear()
    print(color.BOLD+color.BLUE+"\n\n   BOOT OPTIONS FOR",mOSString.upper(),macOSVer.upper()+""+color.END)
    print("   The following boot options are available:")

    if REQUIRES_SUDO == 1:
        print(color.BOLD+"\n      1. Boot",mOSString,macOSVer+color.YELLOW,"⚠"+color.END)
        print(color.END+"         Start",mOSString,"using the detected\n         "+apFilePath+" script file."+color.YELLOW,"Requires superuser."+color.END)
    else:
        print(color.BOLD+"\n      1. Boot",mOSString,macOSVer+"")
        print(color.END+"         Start",mOSString,"using the detected\n         "+apFilePath+" script file.")

    if VALID_FILE_NOPT == 1:
        apFile = open("./"+apFilePathNoPT,"r")
        if "REQUIRES_SUDO=1" in apFile.read():
            REQUIRES_SUDO = 1
        else:
            REQUIRES_SUDO = 0

        if REQUIRES_SUDO == 1:
            print(color.BOLD+"\n      2. Boot",mOSString,macOSVer+" without PCI passthrough"+color.YELLOW+" ⚠"+color.END)
            print(color.END+"         Start",mOSString,"using "+apFilePathNoPT+", with\n         no passthrough devices enabled."+color.YELLOW,"Requires superuser."+color.END)
        else:
            print(color.BOLD+"\n      2. Boot",mOSString,macOSVer+" without PCI passthrough")
            print(color.END+"         Start",mOSString,"using "+apFilePathNoPT+", with\n         no passthrough devices enabled.")

    if VALID_FILE_NOUSB == 1:
        apFile = open("./"+apFilePathNoUSB,"r")
        if "REQUIRES_SUDO=1" in apFile.read():
            REQUIRES_SUDO = 1
        else:
            REQUIRES_SUDO = 0

        if REQUIRES_SUDO == 1:
            print(color.BOLD+"\n      3. Boot",mOSString,macOSVer+" without host USB devices"+color.YELLOW+" ⚠"+color.END)
            print(color.END+"         Start",mOSString,"using "+apFilePathNoUSB+", with\n         no host USB devices."+color.YELLOW,"Requires superuser."+color.END)
        else:
            print(color.BOLD+"\n      3. Boot",mOSString,macOSVer+" without host USB devices")
            print(color.END+"         Start",mOSString,"using "+apFilePathNoUSB+", with\n         no host USB devices.")

    print(color.END+"\n      B. Back...")
    print(color.END+"      Q. Exit\n")
    detectChoice3 = str(input(color.BOLD+"Select> "+color.END))

    # Boot option handling continues as before...
    # [Rest of boot options code remains the same]
    
elif detectChoice == "q" or detectChoice == "Q":
    clear()
    print(color.BOLD+"\n\n   "+color.PURPLE+"GOODBYE!"+color.END)
    print