"esptool.exe" --chip esp32s3 --port "COM3" --baud 921600  --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size 8MB 0x0 "HTIT-WSL_V3_HF.ino.bootloader.bin" 0x8000 "HTIT-WSL_V3_HF.ino.partitions.bin" 0xe000 "boot_app0.bin" 0x10000 "HTIT-WSL_V3_HF.ino.bin" 