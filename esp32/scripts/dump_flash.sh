#!/usr/bin/env bash
# dump_flash.sh - Backup ESP32-S3 external SPI flash using esptool.py
# Requirements: esptool.py (pip install esptool)

set -euo pipefail

CHIP="esp32s3"
PORT="${ESPPORT:-}"
BAUD="${ESPBAUD:-921600}"
SIZE=""            # e.g. 4M, 8M, 16M, or bytes. If empty, attempt auto-detect.
OFFSET="0"         # e.g. 0, 0x0
OUTPUT=""          # If empty, generate based on date/time
GZIP="1"
FORCE="0"

# --- Logging helpers --------------------------------------------------------
ts() { date '+%Y-%m-%d %H:%M:%S'; }
STEP=0
step() { STEP=$(( STEP + 1 )); echo "==> [$(ts)] Step ${STEP}: $*"; }
info() { echo "    [$(ts)] $*"; }
warn() { echo "    [$(ts)] WARNING: $*" >&2; }

usage() {
    echo "Usage: $0 [-p PORT] [-b BAUD] [-s SIZE] [-O OFFSET] [-o OUTPUT] [--gzip] [--force]"
    echo "  -p, --port     Serial port (default: auto-detect from /dev/ttyACM* or /dev/ttyUSB*)"
    echo "  -b, --baud     Baud rate (default: ${BAUD})"
    echo "  -s, --size     Flash size to read, e.g. 4M, 8M, 16M, or bytes. If omitted, try detect."
    echo "  -O, --offset   Start offset (default: 0)"
    echo "  -o, --output   Output filename (default: flash_YYYYmmdd_HHMMSS.bin)"
    echo "      --gzip     Gzip the resulting .bin (default: enabled)"
    echo "      --no-gzip  Do not gzip the resulting .bin"
    echo "      --force    Overwrite existing output file"
    echo "Examples:"
    echo "  $0 -p /dev/ttyACM0 -s 8M -o backup.bin"
    echo "  $0 --no-gzip          (auto-detect port and size, do not gzip)"
    exit 1
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

die() { echo "Error: $*" >&2; exit 1; }

parse_size() {
    # Accept integers, hex (0x...), and suffixes K/M/G (binary: *1024)
    local s="${1:-}"
    [[ -z "$s" ]] && echo "" && return 0
    if [[ "$s" =~ ^0x[0-9A-Fa-f]+$ ]]; then
        printf "%d" "$((s))"
    elif [[ "$s" =~ ^[0-9]+$ ]]; then
        printf "%d" "$s"
    elif [[ "$s" =~ ^([0-9]+)([KkMmGg])$ ]]; then
        local n="${BASH_REMATCH[1]}"
        local u="${BASH_REMATCH[2]}"
        case "$u" in
            K|k) printf "%d" "$(( n * 1024 ))" ;;
            M|m) printf "%d" "$(( n * 1024 * 1024 ))" ;;
            G|g) printf "%d" "$(( n * 1024 * 1024 * 1024 ))" ;;
        esac
    else
        die "Invalid size format: $s"
    fi
}

bytes_to_h() {
    # Pretty print bytes as human-readable binary units
    local b="$1"
    local unit=("B" "KiB" "MiB" "GiB")
    local i=0
    local v="$b"
    while (( v >= 1024 && i < 3 )); do
        v=$(( (v + 512) / 1024 ))
        ((i++))
    done
    echo "${v}${unit[$i]}"
}

autodetect_port() {
    local ports=()
    while IFS= read -r -d '' p; do ports+=("$p"); done < <(ls -1 /dev/ttyACM* /dev/ttyUSB* 2>/dev/null | xargs -r -n1 -0 printf '%s\0')
    if [[ ${#ports[@]} -eq 0 ]]; then
        die "No serial ports found. Specify with -p /dev/ttyACM0 (press BOOT while plugging in if needed)."
    elif [[ ${#ports[@]} -eq 1 ]]; then
        echo "${ports[0]}"
    else
        echo "Multiple serial ports found:" >&2
        printf '  %s\n' "${ports[@]}" >&2
        die "Please specify one with -p."
    fi
}

detect_flash_size_bytes() {
    # Try esptool flash-id and parse 'Detected flash size: XMB' line
    local tmp
    tmp="$(mktemp)"
    # no-reset here avoids toggling after detection; the next command will reconnect anyway
    # Send tool output to stderr so function stdout stays clean for the numeric size
    if "$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" --before default-reset --after no-reset flash-id | tee "$tmp" >&2; then
        :
    else
        rm -f "$tmp"
        return 1
    fi
    local mb
    mb="$(grep -Eo 'Detected flash size: [0-9]+MB' "$tmp" | awk '{print $4}' | tr -d 'MB')"
    rm -f "$tmp"
    if [[ -n "${mb:-}" ]]; then
        printf "%d" "$(( mb * 1024 * 1024 ))"
        return 0
    fi
    return 1
}

# Parse args
ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port) PORT="$2"; shift 2 ;;
        -b|--baud) BAUD="$2"; shift 2 ;;
        -s|--size) SIZE="$2"; shift 2 ;;
        -O|--offset) OFFSET="$2"; shift 2 ;;
        -o|--output) OUTPUT="$2"; shift 2 ;;
        --chip) CHIP="$2"; shift 2 ;;
        --gzip) GZIP="1"; shift ;;
        --no-gzip) GZIP="0"; shift ;;
        --force) FORCE="1"; shift ;;
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

step "Checking prerequisites (esptool)"
info "Using esptool binary: $(command -v "$ESPTOOL")"
info "esptool version: $($ESPTOOL --version 2>&1 | head -n1 || echo unknown)"

# Port
if [[ -z "${PORT:-}" ]]; then
    step "Detecting serial port"
    info "Looking for /dev/ttyACM* or /dev/ttyUSB* (hold BOOT while plugging in if needed)"
    PORT="$(autodetect_port)"
fi
info "Serial port: ${PORT}"

# Offset
step "Parsing start offset"
OFFSET_BYTES="$(parse_size "$OFFSET")"
info "Offset (bytes): ${OFFSET_BYTES}"

# Output
step "Preparing output filename"
if [[ -z "${OUTPUT:-}" ]]; then
    ts="$(date +%Y%m%d_%H%M%S)"
    OUTPUT="flash_${CHIP}_${ts}.bin"
fi
if [[ -e "$OUTPUT" && "$FORCE" != "1" ]]; then
    die "Output file exists: $OUTPUT (use --force to overwrite)"
fi
info "Output path: ${OUTPUT}"

# Size: detect if not provided
if [[ -z "${SIZE:-}" ]]; then
    step "Determining flash size"
    info "Querying target with: flash-id"
    if SIZE_BYTES="$(detect_flash_size_bytes)"; then
        SIZE="$SIZE_BYTES"
        info "Detected: $(bytes_to_h "$SIZE")"
    else
        warn "Auto-detect failed; defaulting to 8 MiB"
        SIZE="8M"
    fi
fi
SIZE_BYTES="$(parse_size "$SIZE")"

step "Summary"
echo "  Chip   : $CHIP"
echo "  Port   : $PORT"
echo "  Baud   : $BAUD"
echo "  Offset : $OFFSET_BYTES bytes"
echo "  Size   : $SIZE_BYTES bytes ($(bytes_to_h "$SIZE_BYTES"))"
echo "  Output : $OUTPUT"

# Read flash
step "Reading flash contents (this may take a while)"
SECONDS=0
set -x
"$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" read_flash "$OFFSET_BYTES" "$SIZE_BYTES" "$OUTPUT"
set +x
info "Read completed in ${SECONDS}s"

# Verify size
step "Verifying output size"
actual_size="$(stat -c%s "$OUTPUT" 2>/dev/null || echo 0)"
if [[ "$actual_size" -ne "$SIZE_BYTES" ]]; then
    warn "Output file size ($actual_size) differs from expected ($SIZE_BYTES)."
fi

# Checksum
if have_cmd sha256sum; then
    step "Computing checksum (SHA256)"
    sha256sum "$OUTPUT" || true
fi

# Optional gzip
if [[ "$GZIP" == "1" ]]; then
    step "Compressing output with gzip"
    gzip -f "$OUTPUT"
    echo "Compressed to ${OUTPUT}.gz"
fi

step "Completed"
echo "Done."