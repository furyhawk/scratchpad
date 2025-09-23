#!/usr/bin/env bash
# flash_latest.sh - Flash ESP32/ESP32-S3 from the latest compressed/full .bin image
#
# Features:
#  - Auto-detect the latest flash_*.bin.gz (or .bin) in a directory
#  - Decompress .gz to a temp file and flash at a chosen offset (default 0x0)
#  - Auto-detect serial port (/dev/ttyACM* or /dev/ttyUSB*)
#  - Safety checks: esptool presence, size vs flash capacity, confirmation prompt
#  - Options to override chip, port, baud, input, dir, offset, erase, non-interactive
#
# Requirements: esptool.py (pip install esptool), gzip

set -euo pipefail

CHIP="esp32s3"           # default chip; override with --chip esp32, esp32s2, etc.
PORT="${ESPPORT:-}"
BAUD="${ESPBAUD:-921600}"
OFFSET="0"               # write offset (0, 0x0, 0x10000, 64K, 1M, etc.)
INPUT=""                 # an explicit input .bin or .bin.gz
SEARCH_DIR="${FWDIR:-}"  # where to search for latest image; defaults to CWD
ERASE="0"                # run erase_flash before writing
YES="0"                  # non-interactive yes to prompts
KEEP_EXTRACT="0"         # keep decompressed temp file
FORCE="0"                # force proceed on certain warnings

# --- Logging helpers --------------------------------------------------------
ts() { date '+%Y-%m-%d %H:%M:%S'; }
STEP=0
step() { STEP=$(( STEP + 1 )); echo "==> [$(ts)] Step ${STEP}: $*"; }
info() { echo "    [$(ts)] $*"; }
warn() { echo "    [$(ts)] WARNING: $*" >&2; }
die() { echo "Error: $*" >&2; exit 1; }

usage() {
    cat <<EOF
Usage: $0 [options]

Options:
  -i, --input FILE     Path to firmware image (.bin or .bin.gz). If omitted, auto-pick latest.
  -d, --dir DIR        Directory to search for latest flash_*.bin.gz (default: current directory).
  -p, --port PORT      Serial port (default: auto-detect /dev/ttyACM* or /dev/ttyUSB*).
  -b, --baud BAUD      Baud rate for esptool (default: ${BAUD}).
  -O, --offset OFF     Write offset (default: 0). Accepts bytes, 0xHEX, or K/M/G suffix.
      --chip NAME      Chip target (default: ${CHIP}).
      --erase          Erase entire flash before writing (esptool erase_flash).
      --yes            Assume yes for prompts (non-interactive).
      --keep           Keep extracted .bin (when input is .gz).
      --force          Proceed despite non-fatal warnings (e.g., size mismatch within flash capacity).
  -h, --help           Show this help and exit.

Examples:
  $0                        # auto-pick latest flash_*.bin.gz in CWD and flash at 0x0
  $0 -d ../backups          # search another directory
  $0 -i build/app.bin -O 0x10000  # flash an app-only image at 0x10000
  $0 -p /dev/ttyACM0 --erase --yes
EOF
}

have_cmd() { command -v "$1" >/dev/null 2>&1; }

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
    if "$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" --before default-reset --after no-reset flash_id 2>&1 | tee "$tmp" >/dev/null; then
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

pick_latest_image() {
    local dir="$1"
    local cand=()
    # Prefer flash_*.bin.gz, then any *.bin.gz, then flash_*.bin, then any *.bin
    for pat in "flash_*.bin.gz" "*.bin.gz" "flash_*.bin" "*.bin"; do
        while IFS= read -r -d '' f; do cand+=("$f"); done < <(find "$dir" -maxdepth 1 -type f -name "$pat" -printf '%T@ %p\0' 2>/dev/null | sort -z -n | awk -v RS='\0' '{print $2"\0"}')
        if [[ ${#cand[@]} -gt 0 ]]; then
            echo "${cand[-1]}"
            return 0
        fi
    done
    return 1
}

# --- Parse args -------------------------------------------------------------
ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--input) INPUT="$2"; shift 2 ;;
        -d|--dir) SEARCH_DIR="$2"; shift 2 ;;
        -p|--port) PORT="$2"; shift 2 ;;
        -b|--baud) BAUD="$2"; shift 2 ;;
        -O|--offset) OFFSET="$2"; shift 2 ;;
        --chip) CHIP="$2"; shift 2 ;;
        --erase) ERASE="1"; shift ;;
        --yes) YES="1"; shift ;;
        --keep) KEEP_EXTRACT="1"; shift ;;
        --force) FORCE="1"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
    esac
done

# --- Prereqs ----------------------------------------------------------------
ESPTOOL=""
if have_cmd esptool; then ESPTOOL="esptool"
elif have_cmd esptool.py; then ESPTOOL="esptool.py"
else die "esptool not found. Install with: pip install esptool"; fi

step "Checking prerequisites (esptool)"
info "Using esptool binary: $(command -v "$ESPTOOL")"
info "esptool version: $($ESPTOOL --version 2>&1 | head -n1 || echo unknown)"

# Determine search dir
if [[ -z "${SEARCH_DIR:-}" ]]; then
    SEARCH_DIR="$(pwd)"
fi

# Port detection
if [[ -z "${PORT:-}" ]]; then
    step "Detecting serial port"
    info "Looking for /dev/ttyACM* or /dev/ttyUSB* (hold BOOT while plugging in if needed)"
    PORT="$(autodetect_port)"
fi
info "Serial port: ${PORT}"

# Offset parse
step "Parsing write offset"
OFFSET_BYTES="$(parse_size "$OFFSET")"
info "Offset (bytes): ${OFFSET_BYTES}"

# Pick input file if not provided
BIN_SRC=""
if [[ -n "${INPUT:-}" ]]; then
    BIN_SRC="$INPUT"
    [[ -f "$BIN_SRC" ]] || die "Input file not found: $BIN_SRC"
else
    step "Selecting latest firmware image"
    info "Searching in: $SEARCH_DIR"
    if BIN_SRC="$(pick_latest_image "$SEARCH_DIR")"; then
        :
    else
        # try script dir as fallback
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        warn "No images found in $SEARCH_DIR; trying $SCRIPT_DIR"
        BIN_SRC="$(pick_latest_image "$SCRIPT_DIR" || true)"
        [[ -n "$BIN_SRC" ]] || die "No suitable .bin or .bin.gz found. Provide --input or --dir."
    fi
fi
info "Selected image: $BIN_SRC"

# If gz, extract to temp; else use directly
TEMP_BIN=""
BIN_TO_FLASH="$BIN_SRC"
if [[ "$BIN_SRC" == *.gz ]]; then
    step "Decompressing gzip image to temporary file"
    have_cmd gzip || die "gzip not found"
    TEMP_BIN="$(mktemp --suffix .bin)"
    info "Extracting to: $TEMP_BIN"
    gzip -dc "$BIN_SRC" > "$TEMP_BIN"
    BIN_TO_FLASH="$TEMP_BIN"
fi

# Determine sizes
BIN_SIZE="$(stat -c%s "$BIN_TO_FLASH" 2>/dev/null || echo 0)"
[[ "$BIN_SIZE" -gt 0 ]] || die "Failed to determine input size for $BIN_TO_FLASH"
info "Image size: ${BIN_SIZE} bytes ($(bytes_to_h "$BIN_SIZE"))"

# Detect flash capacity
step "Detecting target flash capacity"
if FLASH_SIZE_BYTES="$(detect_flash_size_bytes)"; then
    info "Detected flash size: $(bytes_to_h "$FLASH_SIZE_BYTES")"
    # Rough safety check: image must fit from offset
    if (( BIN_SIZE + OFFSET_BYTES > FLASH_SIZE_BYTES )); then
        if [[ "$FORCE" == "1" ]]; then
            warn "Image (size+offset) exceeds detected flash size; proceeding due to --force"
        else
            die "Image (size+offset) exceeds detected flash size ($(bytes_to_h "$FLASH_SIZE_BYTES"))"
        fi
    fi
else
    warn "Could not detect flash size automatically. Proceeding."
fi

# Summary and confirmation
step "Summary"
echo "  Chip     : $CHIP"
echo "  Port     : $PORT"
echo "  Baud     : $BAUD"
echo "  Offset   : $OFFSET_BYTES bytes (0x$(printf '%x' "$OFFSET_BYTES"))"
echo "  Image    : $BIN_SRC"
[[ -n "$TEMP_BIN" ]] && echo "  Extracted: $BIN_TO_FLASH"
echo "  Size     : $BIN_SIZE bytes ($(bytes_to_h "$BIN_SIZE"))"
[[ "$ERASE" == "1" ]] && echo "  Erase    : yes (erase_flash before write)" || echo "  Erase    : no"

if [[ "$YES" != "1" ]]; then
    read -r -p "Proceed with flashing? [y/N] " REPLY
    case "$REPLY" in
        y|Y|yes|YES) ;;
        *)
            info "Aborted by user."
            [[ -n "$TEMP_BIN" && "$KEEP_EXTRACT" != "1" ]] && rm -f "$TEMP_BIN"
            exit 0
            ;;
    esac
fi

# Optional erase
if [[ "$ERASE" == "1" ]]; then
    step "Erasing entire flash"
    set -x
    "$ESPTOOL" --chip "$CHIP" --port "$PORT" --baud "$BAUD" --before default-reset --after no-reset erase_flash
    { set +x; } 2>/dev/null
fi

# Write flash
step "Writing image to flash (this may take a while)"
SECONDS=0
set -x
"$ESPTOOL" \
  --chip "$CHIP" \
  --port "$PORT" \
  --baud "$BAUD" \
  --before default-reset \
  --after hard-reset \
  write_flash \
  -fm keep -fs detect \
  "$OFFSET_BYTES" "$BIN_TO_FLASH"
{ set +x; } 2>/dev/null
info "Flashing completed in ${SECONDS}s"

# Post-verify size written is not trivially possible without readback; optionally suggest it
step "Done"
info "If needed, verify with: esptool --chip $CHIP --port $PORT read_flash $OFFSET_BYTES $BIN_SIZE verify.bin"

# Cleanup
if [[ -n "$TEMP_BIN" && "$KEEP_EXTRACT" != "1" ]]; then
    info "Removing temporary file: $TEMP_BIN"
    rm -f "$TEMP_BIN"
fi

exit 0
