#!/usr/bin/env bash
# flash_tef6686.sh - ESP32 TEF6686 firmware upgrade script
# Converted from Windows batch file
# v2.0.15 (mod16 by Megatron) - Linux version

set -euo pipefail

# Default values
CHIP="esp32"
BAUD="921600"
FLASH_MODE="dio"
FLASH_FREQ="80m"
FLASH_SIZE="4MB"

# Firmware files (expected to be in the same directory as this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTLOADER_BIN="${SCRIPT_DIR}/bootloader.bin"
PARTITIONS_BIN="${SCRIPT_DIR}/partitions.bin"
BOOT_APP0_BIN="${SCRIPT_DIR}/boot_app0.bin"
TEF6686_BIN="${SCRIPT_DIR}/TEF6686_ESP32.ino.bin"
SPIFFS_BIN="${SCRIPT_DIR}/TEF6686_ESP32.spiffs.bin"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging helpers
info() { echo -e "${BLUE}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }

print_header() {
    clear
    echo "****************************************************************"
    echo "*                    ESP32 TEF6686固件升级                     *"
    echo "*                  v2.0.15(mod16 by Megatron)                  *"
    echo "*                      Linux版本                               *"
    echo "****************************************************************"
    echo
}

check_dependencies() {
    if ! command -v esptool >/dev/null 2>&1 && ! command -v esptool.py >/dev/null 2>&1; then
        error "esptool not found. Please install it:"
        echo "  pip install esptool"
        echo "  or"
        echo "  sudo apt-get install esptool"
        exit 1
    fi
}

check_firmware_files() {
    local missing_files=()
    
    for file in "$BOOTLOADER_BIN" "$PARTITIONS_BIN" "$BOOT_APP0_BIN" "$TEF6686_BIN" "$SPIFFS_BIN"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$(basename "$file")")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        error "Missing firmware files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        echo "Please ensure all firmware files are in the script directory: $SCRIPT_DIR"
        exit 1
    fi
}

list_serial_ports() {
    local ports=()
    
    # Look for common ESP32 serial devices
    for device in /dev/ttyUSB* /dev/ttyACM* /dev/cu.usbserial* /dev/cu.SLAB_USBtoUART* /dev/cu.wchusbserial*; do
        if [[ -e "$device" ]]; then
            ports+=("$device")
        fi
    done
    
    if [[ ${#ports[@]} -eq 0 ]]; then
        warn "No serial ports detected. Common ESP32 ports are:"
        echo "  - /dev/ttyUSB0, /dev/ttyUSB1, ..."
        echo "  - /dev/ttyACM0, /dev/ttyACM1, ..."
        echo "  - /dev/cu.usbserial-* (macOS)"
        echo
        return 1
    fi
    
    echo "Available serial ports:"
    for i in "${!ports[@]}"; do
        echo "  $((i+1)) = ${ports[i]}"
    done
    echo
    return 0
}

select_port() {
    local port=""
    
    echo "Please ensure your device is connected in flash mode!" >&2
    echo >&2
    
    if list_serial_ports >&2; then
        while true; do
            read -p "Enter port number or full path (e.g., 1 or /dev/ttyUSB0): " input
            
            if [[ "$input" =~ ^[0-9]+$ ]]; then
                # User entered a number
                local ports=()
                for device in /dev/ttyUSB* /dev/ttyACM* /dev/cu.usbserial* /dev/cu.SLAB_USBtoUART* /dev/cu.wchusbserial*; do
                    if [[ -e "$device" ]]; then
                        ports+=("$device")
                    fi
                done
                
                local index=$((input-1))
                if [[ $index -ge 0 && $index -lt ${#ports[@]} ]]; then
                    port="${ports[index]}"
                    break
                else
                    error "Invalid selection. Please choose a number between 1 and ${#ports[@]}."
                fi
            elif [[ -e "$input" ]]; then
                # User entered a full path
                port="$input"
                break
            else
                error "Port '$input' does not exist. Please try again."
            fi
        done
    else
        # No ports auto-detected, ask user to enter manually
        while true; do
            read -p "Enter serial port path (e.g., /dev/ttyUSB0): " port
            if [[ -e "$port" ]]; then
                break
            else
                error "Port '$port' does not exist. Please try again."
            fi
        done
    fi
    
    echo "$port"
}

flash_firmware() {
    local port="$1"
    
    info "Starting firmware upgrade, please do not disconnect..."
    echo
    
    # Build esptool command
    local cmd=(
        esptool
        --chip "$CHIP"
        --port "$port"
        --baud "$BAUD"
        --before default-reset
        --after hard-reset
        write-flash
        -z
        --flash-mode "$FLASH_MODE"
        --flash-freq "$FLASH_FREQ"
        --flash-size "$FLASH_SIZE"
        0x1000 "$BOOTLOADER_BIN"
        0x8000 "$PARTITIONS_BIN"
        0xe000 "$BOOT_APP0_BIN"
        0x10000 "$TEF6686_BIN"
        0x00310000 "$SPIFFS_BIN"
    )
    
    # Show command being executed (for debugging)
    info "Executing: ${cmd[*]}"
    echo
    
    # Execute the flash command
    if "${cmd[@]}"; then
        echo
        success "Firmware upgrade completed successfully!"
        return 0
    else
        echo
        error "Firmware upgrade failed! Please check device and serial port status."
        return 1
    fi
}

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "ESP32 TEF6686 Firmware Upgrade Tool"
    echo
    echo "Options:"
    echo "  -p, --port PORT     Specify serial port (interactive selection if not provided)"
    echo "  -b, --baud RATE     Set baud rate (default: $BAUD)"
    echo "  -h, --help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0                  # Interactive mode"
    echo "  $0 -p /dev/ttyUSB0  # Use specific port"
    echo "  $0 --baud 115200    # Use different baud rate"
}

main() {
    local port=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                port="$2"
                shift 2
                ;;
            -b|--baud)
                BAUD="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    print_header
    check_dependencies
    check_firmware_files
    
    # Select port if not provided
    if [[ -z "$port" ]]; then
        port=$(select_port)
    elif [[ ! -e "$port" ]]; then
        error "Specified port '$port' does not exist."
        exit 1
    fi
    
    info "Using port: $port"
    echo
    
    # Flash the firmware
    if flash_firmware "$port"; then
        echo
        success "All done! You can now disconnect your device."
        if [[ -t 0 ]]; then
            read -p "Press Enter to exit..."
        fi
    else
        exit 1
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi