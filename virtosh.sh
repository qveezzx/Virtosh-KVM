#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_NAME=$NAME
    else
        print_error "Cannot detect distribution"
        exit 1
    fi

    print_info "Detected distribution: $DISTRO_NAME"

    if command -v yay &> /dev/null; then
        PKG_MANAGER="yay"
        INSTALL_CMD="yay -S --noconfirm"
        CHECK_CMD="yay -Qi"
    elif command -v paru &> /dev/null; then
        PKG_MANAGER="paru"
        INSTALL_CMD="paru -S --noconfirm"
        CHECK_CMD="paru -Qi"
    elif command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
        CHECK_CMD="pacman -Qi"
    elif command -v apt &> /dev/null; then
        PKG_MANAGER="apt"
        INSTALL_CMD="sudo apt install -y"
        CHECK_CMD="dpkg -s"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        INSTALL_CMD="sudo dnf install -y"
        CHECK_CMD="rpm -q"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        INSTALL_CMD="sudo yum install -y"
        CHECK_CMD="rpm -q"
    elif command -v zypper &> /dev/null; then
        PKG_MANAGER="zypper"
        INSTALL_CMD="sudo zypper install -y"
        CHECK_CMD="rpm -q"
    elif command -v apk &> /dev/null; then
        PKG_MANAGER="apk"
        INSTALL_CMD="sudo apk add"
        CHECK_CMD="apk info -e"
    elif command -v emerge &> /dev/null; then
        PKG_MANAGER="emerge"
        INSTALL_CMD="sudo emerge --ask=n"
        CHECK_CMD="qlist -I"
    elif command -v xbps-install &> /dev/null; then
        PKG_MANAGER="xbps"
        INSTALL_CMD="sudo xbps-install -Sy"
        CHECK_CMD="xbps-query -l"
    elif command -v pkg &> /dev/null; then
        PKG_MANAGER="pkg"
        INSTALL_CMD="sudo pkg install -y"
        CHECK_CMD="pkg info"
    elif command -v pkg_add &> /dev/null; then
        PKG_MANAGER="pkg_add"
        INSTALL_CMD="sudo pkg_add"
        CHECK_CMD="pkg_info"
    else
        print_error "No supported package manager found"
        exit 1
    fi

    print_info "Using package manager: $PKG_MANAGER"
}

get_package_name() {
    local generic_name=$1

    case $PKG_MANAGER in
        pacman|yay|paru)
            case $generic_name in
                qemu-full) echo "qemu-full" ;;
                libvirt) echo "libvirt" ;;
                dnsmasq) echo "dnsmasq" ;;
                python) echo "python" ;;
                virt-manager) echo "virt-manager" ;;
                nbd) echo "nbd" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        apt)
            case $generic_name in
                qemu-full) echo "qemu-system qemu-utils" ;;
                libvirt) echo "libvirt-daemon-system libvirt-clients" ;;
                dnsmasq) echo "dnsmasq" ;;
                python) echo "python3" ;;
                virt-manager) echo "virt-manager" ;;
                nbd) echo "nbd-client" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        dnf|yum)
            case $generic_name in
                qemu-full) echo "qemu-kvm qemu-img" ;;
                libvirt) echo "libvirt libvirt-daemon-kvm" ;;
                dnsmasq) echo "dnsmasq" ;;
                python) echo "python3" ;;
                virt-manager) echo "virt-manager" ;;
                nbd) echo "nbd" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        zypper)
            case $generic_name in
                qemu-full) echo "qemu qemu-tools" ;;
                libvirt) echo "libvirt libvirt-daemon" ;;
                dnsmasq) echo "dnsmasq" ;;
                python) echo "python3" ;;
                virt-manager) echo "virt-manager" ;;
                nbd) echo "nbd" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        apk)
            case $generic_name in
                qemu-full) echo "qemu" ;;
                libvirt) echo "libvirt" ;;
                dnsmasq) echo "dnsmasq" ;;
                python) echo "python3" ;;
                virt-manager) echo "virt-manager" ;;
                nbd) echo "nbd" ;;
                *) echo "$generic_name" ;;
            esac
            ;;
        emerge|xbps|pkg|pkg_add)
            echo "$generic_name"
            ;;
    esac
}

command_exists() { command -v "$1" &> /dev/null; }

check_dependency() {
    local dep_name=$1
    local cmd_name=$2
    local pkg_name=$3
    local optional=$4

    print_info "Checking $dep_name..."

    if command_exists "$cmd_name"; then
        print_success "$dep_name is already installed"
        return 0
    else
        if [ "$optional" = "true" ]; then
            print_warning "$dep_name is not installed (optional)"
            return 1
        else
            local packages=$(get_package_name "$pkg_name")
            print_info "Installing $dep_name ($packages)..."
            echo "-------------------"
            echo "Installing: $packages"
            echo "-------------------"
            eval "$INSTALL_CMD $packages"
            
            if command_exists "$cmd_name"; then
                print_success "$dep_name installed successfully"
                return 0
            else
                print_error "Failed to install $dep_name"
                return 1
            fi
        fi
    fi
}

main() {
    echo "=========================================="
    echo "          Virtosh Package Check"
    echo "=========================================="
    echo

    detect_distro
    echo

    print_info "Checking required dependencies..."
    echo
    check_dependency "Sudo" "sudo" "sudo" "false"
    check_dependency "Git" "git" "git" "false"
    check_dependency "Wget" "wget" "wget" "false"
    check_dependency "QEMU" "qemu-system-x86_64" "qemu-full" "false"
    check_dependency "Libvirt" "virsh" "libvirt" "false"
    check_dependency "DNSmasq" "dnsmasq" "dnsmasq" "false"
    check_dependency "Python" "python3" "python" "false"
    
    echo
    print_info "Checking optional dependencies..."
    echo
    check_dependency "Virt-Manager" "virt-manager" "virt-manager" "true"

    echo
    print_info "Starting libvirt service..."
    if systemctl is-active --quiet libvirtd; then
        print_success "libvirtd is already running"
    else
        sudo systemctl start libvirtd
        sudo systemctl enable libvirtd
        print_success "libvirtd started and enabled"
    fi

    echo
    print_success "All required dependencies are installed!"
    echo

    if [ -f "./main.py" ]; then
        print_info "Found main.py, executing in 2 seconds..."
        sleep 2
        python3 ./main.py
    else
        print_error "main.py not found in current directory"
        exit 1
    fi
}

main
