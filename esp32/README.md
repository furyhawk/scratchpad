## ESP32 Utilities

This folder contains helper scripts for working with ESP32/ESP32‑S3 devices:

- `scripts/flash_latest.sh` — Flash your board from the latest compressed/full firmware image.
- `scripts/dump_flash.sh` — Create a backup of the device external SPI flash.

Both scripts use `esptool.py` under the hood and work on Linux.

### Prerequisites

- Python and esptool
	- Install: `pip install esptool`
- Access to the serial device (e.g., `/dev/ttyACM0` or `/dev/ttyUSB0`)
	- If you see permission errors, add your user to the `dialout` group or run with `sudo`.

---

## Flash from latest image — `scripts/flash_latest.sh`

Flashes the ESP32/ESP32‑S3 from the most recent `flash_*.bin.gz` (or `.bin`) found in a directory. If the image is gzipped, it will be decompressed to a temporary file automatically.

Key features:

- Auto-detect latest image in a directory (prefers `flash_*.bin.gz`).
- Auto-detect serial port from `/dev/ttyACM*` or `/dev/ttyUSB*`.
- Flexible offset parsing (e.g., `0x0`, `0x10000`, `64K`, `1M`).
- Optional full-chip erase before flashing.
- Safety checks against detected flash capacity (when available).

Usage:

```bash
./esp32/scripts/flash_latest.sh [options]
```

Options:

- `-i, --input FILE`  Use a specific image file (`.bin` or `.bin.gz`).
- `-d, --dir DIR`     Directory to search for the latest image (default: current dir).
- `-p, --port PORT`   Serial device (auto-detected if omitted).
- `-b, --baud BAUD`   Baud rate for esptool (default: 921600).
- `-O, --offset OFF`  Write offset (default: `0`). Accepts bytes, `0xHEX`, `K/M/G` suffixes.
- `--chip NAME`       Chip target (default: `esp32s3`).
- `--erase`           Erase entire flash before writing.
- `--yes`             Non-interactive confirmation.
- `--keep`            Keep extracted `.bin` when input is `.gz`.
- `--force`           Proceed despite non-fatal warnings.

Environment variables (optional):

- `ESPPORT` sets default serial port (e.g., `/dev/ttyACM0`).
- `ESPBAUD` sets default baud (e.g., `921600`).
- `FWDIR` sets a default search directory for images.

Examples:

```bash
# Flash the most recent flash_*.bin.gz in the current directory at offset 0x0
./esp32/scripts/flash_latest.sh

# Search a different directory for the latest image
./esp32/scripts/flash_latest.sh -d ./firmware_backups

# Flash a specific app image at 0x10000
./esp32/scripts/flash_latest.sh -i ./build/app.bin -O 0x10000

# Specify port, erase first, and skip prompts
./esp32/scripts/flash_latest.sh -p /dev/ttyACM0 --erase --yes
```

Notes:

- Typical single‑image offsets use `0x0`.
- For partitioned builds (bootloader/partitions/app), you’ll usually write multiple segments at their respective offsets; this script currently flashes a single image. If you want multi-segment support, open an issue or extend the script.

---

## Backup flash — `scripts/dump_flash.sh`

Creates a complete backup of the external SPI flash to a `.bin` file and optionally gzips it.

Key features:

- Auto-detect serial port and flash size (via `esptool flash-id`).
- Flexible size/offset parsing (e.g., `8M`, `0x0`, `64K`).
- Timestamped output filenames (e.g., `flash_esp32s3_YYYYmmdd_HHMMSS.bin`).

Usage:

```bash
./esp32/scripts/dump_flash.sh [options]
```

Options (highlights):

- `-p, --port PORT`   Serial device (auto-detected if omitted).
- `-b, --baud BAUD`   Baud rate (default: 921600).
- `-s, --size SIZE`   Flash size to read (e.g., `8M`); auto-detect if omitted.
- `-O, --offset OFF`  Start offset (default: `0`).
- `-o, --output FILE` Output filename (default: timestamped).
- `--gzip/--no-gzip`  Enable/disable gzip of the result (default: gzip enabled).
- `--force`           Overwrite existing output file.

Examples:

```bash
# Auto-detect port and full size, write compressed backup
./esp32/scripts/dump_flash.sh

# Specify size and output filename
./esp32/scripts/dump_flash.sh -p /dev/ttyACM0 -s 8M -o backup.bin --no-gzip

# Read a region only
./esp32/scripts/dump_flash.sh -O 0x10000 -s 1M -o app_region.bin
```

---

## Tips & Troubleshooting

- Enter bootloader mode: hold the BOOT button while plugging the USB cable (or press BOOT, tap RST, release BOOT) if the port doesn’t appear.
- Multiple ports found: specify one with `-p /dev/ttyACM0`.
- Permission denied on serial: add your user to the `dialout` group or use `sudo`.
- Size mismatch warnings: ensure you’re flashing the correct image and offset for your device; use `--force` only if you know it’s safe.
- Verifying a flash: you can spot‑check by reading back the region you wrote and comparing hashes.

Example verify:

```bash
# Read back the written region (example: 0x0 for BIN_SIZE bytes)
BIN_SIZE=<bytes_of_image>
esptool --chip esp32s3 --port /dev/ttyACM0 read_flash 0x0 ${BIN_SIZE} verify.bin
sha256sum verify.bin
```

---

## License

See the repository `LICENSE` file.

