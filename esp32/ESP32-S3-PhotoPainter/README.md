# ESP32-S3-PhotoPainter
中文wiki链接: https://www.waveshare.net/wiki/ESP32-S3-PhotoPainter<br>
Product English wiki link: https://www.waveshare.com/wiki/ESP32-S3-PhotoPainter

## Image converter usage

This folder includes a simple converter script (`convert.py`) to prepare images for the PhotoPainter display.

Basic usage (single file):

```bash
python3 convert.py path/to/image.jpg --mode scale --dir landscape
```

Batch convert a directory of images:

```bash
python3 convert.py --input-dir ./images --mode scale --dir landscape
```

Options:

- `image_file` — Optional positional path to a single image.
- `--input-dir DIR` — Directory containing images to convert (mutually exclusive with `image_file`).
- `-r, --recursive` — Recurse into subdirectories when using `--input-dir`.
- `--outdir DIR` — Output directory (defaults to alongside each input file).
- `--dir {landscape,portrait}` — Target orientation; if omitted, orientation is auto‑detected from the image aspect ratio.
- `--mode {scale,cut}` — Scaling behavior. `scale` fits the image with padding; `cut` crops to fill.
- `--dither {0,3}` — Dithering algorithm (`0` = NONE, `3` = FLOYDSTEINBERG). Defaults to FLOYDSTEINBERG.

Outputs are written as BMP files named `<basename>_<mode>_output.bmp`.