#encoding: utf-8

import sys
import os
import os.path
from PIL import Image, ImagePalette, ImageOps
import argparse
from typing import Iterable, List, Tuple

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Convert image(s) for ESP32 PhotoPainter display.')

# Add orientation parameter
parser.add_argument('image_file', nargs='?', type=str, help='Input image file')
parser.add_argument('--input-dir', type=str, help='Directory containing images to convert')
parser.add_argument('-r', '--recursive', action='store_true', help='Recurse into subdirectories when using --input-dir')
parser.add_argument('--outdir', type=str, help='Directory to write outputs (defaults to alongside each input)')
parser.add_argument('--dir', choices=['landscape', 'portrait'], help='Image direction (landscape or portrait)')
parser.add_argument('--mode', choices=['scale', 'cut'], default='scale', help='Image conversion mode (scale or cut)')
parser.add_argument('--dither', type=int, choices=[Image.NONE, Image.FLOYDSTEINBERG], default=Image.FLOYDSTEINBERG, help='Image dithering algorithm (NONE(0) or FLOYDSTEINBERG(3))')

# Parse command line arguments
args = parser.parse_args()

def get_target_size(img: Image.Image, display_direction: str | None) -> Tuple[int, int]:
    width, height = img.size
    if display_direction:
        return (800, 480) if display_direction == 'landscape' else (480, 800)
    # auto based on aspect
    return (800, 480) if width > height else (480, 800)


def convert_single_image(
    input_filename: str,
    display_direction: str | None,
    display_mode: str,
    display_dither: int,
    outdir: str | None,
    pal_image: Image.Image,
) -> Tuple[bool, str]:
    try:
        if not os.path.isfile(input_filename):
            return False, f'Error: file {input_filename} does not exist'

        input_image = Image.open(input_filename)
        target_width, target_height = get_target_size(input_image, display_direction)
        width, height = input_image.size

        if display_mode == 'scale':
            scale_ratio = max(target_width / width, target_height / height)
            resized_width = int(width * scale_ratio)
            resized_height = int(height * scale_ratio)
            output_image = input_image.resize((resized_width, resized_height))
            resized_image = Image.new('RGB', (target_width, target_height), (255, 255, 255))
            left = (target_width - resized_width) // 2
            top = (target_height - resized_height) // 2
            resized_image.paste(output_image, (left, top))
        elif display_mode == 'cut':
            if width / height >= target_width / target_height:
                delta_width = int(height * target_width / target_height - width)
                padding = (delta_width // 2, 0, delta_width - delta_width // 2, 0)
                box = (0, 0, width, height)
            else:
                delta_height = int(width * target_height / target_width - height)
                padding = (0, delta_height // 2, 0, delta_height - delta_height // 2)
                box = (0, 0, width, height)
            # padding is computed but ImageOps.pad handles final canvas
            resized_image = ImageOps.pad(input_image.crop(box), size=(target_width, target_height), color=(255, 255, 255), centering=(0.5, 0.5))
        else:
            return False, f'Unsupported mode: {display_mode}'

        quantized_image = resized_image.quantize(dither=display_dither, palette=pal_image).convert('RGB')

        base = os.path.splitext(os.path.basename(input_filename))[0]
        output_basename = f"{base}_{display_mode}_output.bmp"
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            output_filename = os.path.join(outdir, output_basename)
        else:
            output_filename = os.path.join(os.path.dirname(input_filename), output_basename)

        quantized_image.save(output_filename)
        return True, f'Successfully converted {input_filename} to {output_filename}'
    except Exception as e:
        return False, f'Error converting {input_filename}: {e}'


def iter_image_files(root: str, recursive: bool) -> Iterable[str]:
    exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff'}
    if os.path.isfile(root):
        yield root
        return
    if not os.path.isdir(root):
        return
    if recursive:
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in filenames:
                if os.path.splitext(fn)[1].lower() in exts:
                    yield os.path.join(dirpath, fn)
    else:
        for fn in os.listdir(root):
            full = os.path.join(root, fn)
            if os.path.isfile(full) and os.path.splitext(fn)[1].lower() in exts:
                yield full


def main():
    # Validate input sources
    if not args.image_file and not args.input_dir:
        parser.error('Please provide an image file or --input-dir')
    if args.image_file and args.input_dir:
        parser.error('Please specify only one of image_file or --input-dir')

    display_direction = args.dir
    display_mode = args.mode
    display_dither = Image.Dither(args.dither)

    # Prepare palette once
    pal_image = Image.new("P", (1, 1))
    pal_image.putpalette((0,0,0,  255,255,255,  255,255,0,  255,0,0,  0,0,0,  0,0,255,  0,255,0) + (0,0,0)*249)

    if args.image_file:
        ok, msg = convert_single_image(
            input_filename=args.image_file,
            display_direction=display_direction,
            display_mode=display_mode,
            display_dither=display_dither,
            outdir=args.outdir,
            pal_image=pal_image,
        )
        print(msg)
        sys.exit(0 if ok else 1)

    # Directory mode
    if not os.path.isdir(args.input_dir):
        print(f"Error: directory {args.input_dir} does not exist")
        sys.exit(1)

    total = 0
    success = 0
    failures: List[str] = []
    for img_path in iter_image_files(args.input_dir, args.recursive):
        total += 1
        ok, msg = convert_single_image(
            input_filename=img_path,
            display_direction=display_direction,
            display_mode=display_mode,
            display_dither=display_dither,
            outdir=args.outdir,
            pal_image=pal_image,
        )
        if ok:
            success += 1
        else:
            failures.append(img_path)
        print(msg)

    print(f"\nBatch conversion complete: {success}/{total} succeeded.")
    if failures:
        print("Failed files:")
        for f in failures:
            print(f" - {f}")
    sys.exit(0 if success == total and total > 0 else 1)


if __name__ == '__main__':
    main()

