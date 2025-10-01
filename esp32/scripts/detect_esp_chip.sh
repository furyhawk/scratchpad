#!/usr/bin/env bash
# detect_esp_chip.sh - Detect and display ESP chip information
# Requirements: esptool.py (pip install esptool)

set -euo pipefail

PORT="${ESPPORT:-}"
BAUD="${ESPBAUD:-115200}"
CHIP="${ESPCHIP:-auto}"

# --- Logging helpers --------------------------------------------------------
ts() { date '+%Y-%m-%d %H:%M:%S'; }
STEP=0
step() { STEP=$(( STEP + 1 )); echo "==> [$(ts)] Step ${STEP}: $*"; }
info() { echo "    [$(ts)] $*"; }
warn() { echo "    [$(ts)] WARNING: $*" >&2; }
error() { echo "    [$(ts)] ERROR: $*" >&2; }

usage() {
    echo "Usage: $0 [-p PORT] [-b BAUD] [-c CHIP]"
    echo "  -p, --port     Serial port (default: auto-detect from /dev/ttyACM* or /dev/ttyUSB*)"
    echo "  -b, --baud     Baud rate (default: ${BAUD})"
    echo "  -c, --chip     Chip type (default: auto-detect)"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Auto-detect everything"
    echo "  $0 -p /dev/ttyACM0    # Use specific port"
    echo "  $0 -c esp32s3        # Force specific chip type"
    echo ""
    echo "Environment variables:"
    echo "  ESPPORT    - Default serial port"
    echo "  ESPBAUD    - Default baud rate"
    echo "  ESPCHIP    - Default chip type"
    exit 1
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

die() { echo "Error: $*" >&2; exit 1; }

autodetect_port() {
    local ports=()
    while IFS= read -r -d '' p; do ports+=("$p"); done < <(ls -1 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | xargs -r -n1 -0 printf '%s\0')
    if [[ ${#ports[@]} -eq 0 ]]; then
        die "No serial ports found. Make sure ESP is connected and press BOOT while plugging in if needed."
    elif [[ ${#ports[@]} -eq 1 ]]; then
        echo "${ports[0]}"
    else
        echo "Multiple serial ports found:" >&2
        printf '  %s\n' "${ports[@]}" >&2
        die "Please specify one with -p."
    fi
}

parse_chip_info() {
    # Parse esptool output and extract chip information
    local output_file="$1"
    local chip_type mac_addr flash_size crystal_freq features
    
    echo "=== ESP Chip Information ==="
    echo ""
    
    # Extract chip type
    if chip_type=$(grep -E "Chip is" "$output_file" | sed 's/.*Chip is \([^(]*\).*/\1/' | tr -d ' '); then
        echo "Chip Type       : $chip_type"
    fi
    
    # Extract MAC address
    if mac_addr=$(grep -E "MAC:" "$output_file" | sed 's/.*MAC: \([0-9a-f:]*\).*/\1/'); then
        echo "MAC Address     : $mac_addr"
    fi
    
    # Extract crystal frequency
    if crystal_freq=$(grep -E "Crystal is" "$output_file" | sed 's/.*Crystal is \([0-9]*MHz\).*/\1/'); then
        echo "Crystal Freq    : $crystal_freq"
    fi
    
    # Extract features
    if features=$(grep -E "Features:" "$output_file" | sed 's/.*Features: \(.*\)/\1/'); then
        echo "Features        : $features"
    fi
    
    echo ""
}

parse_flash_info() {
    # Parse flash information from esptool output
    local output_file="$1"
    local flash_id manufacturer device flash_size
    
    echo "=== Flash Memory Information ==="
    echo ""
    
    # Extract flash ID
    if flash_id=$(grep -E "Manufacturer:" "$output_file" | head -1 | sed 's/.*Manufacturer: \([0-9a-f]*\) Device: \([0-9a-f]*\).*/\1:\2/'); then
        echo "Flash ID        : $flash_id"
    fi
    
    # Extract manufacturer
    if manufacturer=$(grep -E "Detected flash size:" "$output_file" | sed 's/.*Detected flash size: \([0-9]*MB\).*/\1/'); then
        echo "Flash Size      : ${manufacturer}MB"
    fi
    
    # Look for flash manufacturer name
    if grep -q "winbond" "$output_file"; then
        echo "Manufacturer    : Winbond"
    elif grep -q "gigadevice" "$output_file"; then
        echo "Manufacturer    : GigaDevice"
    elif grep -q "issi" "$output_file"; then
        echo "Manufacturer    : ISSI"
    elif grep -q "mxic" "$output_file"; then
        echo "Manufacturer    : MXIC"
    fi
    
    echo ""
}

show_connection_info() {
    echo "=== Connection Information ==="
    echo ""
    echo "Serial Port     : $PORT"
    echo "Baud Rate       : $BAUD"
    echo "Chip Override   : $CHIP"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port) PORT="$2"; shift 2 ;;
        -b|--baud) BAUD="$2"; shift 2 ;;
        -c|--chip) CHIP="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown argument: $1" >&2; usage ;;
    esac
done

# Find esptool
ESPTOOL=""
if have_cmd esptool; then ESPTOOL="esptool"
elif have_cmd esptool.py; then ESPTOOL="esptool.py"
else die "esptool not found. Install with: pip install esptool"
fi

step "Checking prerequisites"
info "Using esptool: $(command -v "$ESPTOOL")"
esptool_version=$($ESPTOOL --version 2>&1 | head -n1 || echo "unknown")
info "Version: $esptool_version"

# Auto-detect port if not specified
if [[ -z "${PORT:-}" ]]; then
    step "Detecting serial port"
    info "Looking for /dev/ttyACM* or /dev/ttyUSB*"
    PORT="$(autodetect_port)"
    info "Found: $PORT"
else
    step "Using specified port"
    info "Port: $PORT"
fi

# Verify port exists and is accessible
if [[ ! -e "$PORT" ]]; then
    die "Serial port does not exist: $PORT"
fi

if [[ ! -r "$PORT" || ! -w "$PORT" ]]; then
    warn "Port $PORT may not be accessible. You might need to run with sudo or add user to dialout group."
fi

step "Connecting to ESP chip"
info "Attempting connection (press and hold BOOT button if connection fails)"

# Create temporary file for esptool output
temp_output=$(mktemp)
trap "rm -f '$temp_output'" EXIT

# Run chip_id command to get basic chip information
echo "--- Running chip_id command ---"
if "$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" chip_id 2>&1 | tee "$temp_output"; then
    echo ""
    parse_chip_info "$temp_output"
else
    error "Failed to connect to chip. Make sure:"
    echo "  1. ESP is properly connected to $PORT"
    echo "  2. Press and hold BOOT button while connecting"
    echo "  3. Try a different baud rate with -b option"
    echo "  4. Check if another program is using the port"
    exit 1
fi

# Run flash_id command to get flash information
step "Detecting flash memory"
echo "--- Running flash_id command ---"
if "$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" flash_id 2>&1 | tee -a "$temp_output"; then
    echo ""
    parse_flash_info "$temp_output"
else
    warn "Failed to read flash information"
fi

# Show connection summary
show_connection_info

step "Detection completed"
info "Chip detection successful!"

# Show raw output option
echo "=== Raw Output ==="
echo "Full esptool output saved to: $temp_output"
echo "To view raw output: cat $temp_output"
echo ""
echo "Tip: Use 'esptool --help' to see all available commands for this chip."