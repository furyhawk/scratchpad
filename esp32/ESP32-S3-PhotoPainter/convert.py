#encoding: utf-8

import sys
import os
import os.path
from PIL import Image, ImagePalette, ImageOps
import argparse
from typing import Iterable, List, Tuple
import numpy as np

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Convert image(s) for ESP32 PhotoPainter display.')

# Add orientation parameter
parser.add_argument('image_file', nargs='?', type=str, help='Input image file')
parser.add_argument('--input-dir', type=str, help='Directory containing images to convert')
parser.add_argument('-r', '--recursive', action='store_true', help='Recurse into subdirectories when using --input-dir')
parser.add_argument('--outdir', type=str, help='Directory to write outputs (defaults to alongside each input)')
parser.add_argument('--dir', choices=['landscape', 'portrait'], help='Image direction (landscape or portrait). Auto-detects based on aspect ratio if not specified.')
parser.add_argument('--mode', choices=['scale', 'cut'], default='scale', help='Image conversion mode (scale or cut)')
parser.add_argument('--dither', type=str, choices=['none', 'floyd-steinberg', 'atkinson'], default='floyd-steinberg', help='Image dithering algorithm (none, floyd-steinberg, or atkinson)')

# Parse command line arguments
args = parser.parse_args()

def get_target_size(img: Image.Image, display_direction: str | None) -> Tuple[Tuple[int, int], str]:
    """
    Get target size and orientation for the image.
    Returns: ((width, height), orientation_string)
    """
    width, height = img.size
    if display_direction:
        size = (800, 480) if display_direction == 'landscape' else (480, 800)
        return size, display_direction
    # auto based on aspect
    orientation = 'landscape' if width > height else 'portrait'
    size = (800, 480) if orientation == 'landscape' else (480, 800)
    return size, orientation


def apply_atkinson_dithering(image: Image.Image, palette_image: Image.Image) -> Image.Image:
    """Apply Atkinson dithering algorithm to an image."""
    # Convert to RGB if not already
    img_rgb = image.convert('RGB')
    
    # Get palette colors
    palette = palette_image.getpalette()
    palette_colors = []
    for i in range(0, len(palette), 3):
        if i // 3 < 7:  # We have 7 colors defined
            palette_colors.append((palette[i], palette[i+1], palette[i+2]))
    
    # Convert image to numpy array for faster processing
    img_array = np.array(img_rgb, dtype=np.float32)
    height, width = img_array.shape[:2]
    
    # Process each pixel
    for y in range(height):
        for x in range(width):
            old_pixel = img_array[y, x].copy()
            
            # Find closest palette color
            min_dist = float('inf')
            new_pixel = palette_colors[0]
            for color in palette_colors:
                dist = np.sum((old_pixel - np.array(color)) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    new_pixel = color
            
            img_array[y, x] = new_pixel
            quant_error = old_pixel - np.array(new_pixel)
            
            # Distribute error using Atkinson kernel (divides by 8)
            # Atkinson pattern:
            #         X   1/8 1/8
            #     1/8 1/8 1/8
            #         1/8
            
            if x + 1 < width:
                img_array[y, x + 1] += quant_error * (1/8)
            if x + 2 < width:
                img_array[y, x + 2] += quant_error * (1/8)
            
            if y + 1 < height:
                if x - 1 >= 0:
                    img_array[y + 1, x - 1] += quant_error * (1/8)
                img_array[y + 1, x] += quant_error * (1/8)
                if x + 1 < width:
                    img_array[y + 1, x + 1] += quant_error * (1/8)
            
            if y + 2 < height:
                img_array[y + 2, x] += quant_error * (1/8)
    
    # Clip values and convert back to uint8
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    return Image.fromarray(img_array, 'RGB')



def convert_single_image(
    input_filename: str,
    display_direction: str | None,
    display_mode: str,
    display_dither: str,
    outdir: str | None,
    pal_image: Image.Image,
) -> Tuple[bool, str]:
    try:
        if not os.path.isfile(input_filename):
            return False, f'Error: file {input_filename} does not exist'

        input_image = Image.open(input_filename)
        (target_width, target_height), detected_orientation = get_target_size(input_image, display_direction)
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

        # Apply dithering based on selected algorithm
        if display_dither == 'atkinson':
            quantized_image = apply_atkinson_dithering(resized_image, pal_image)
        elif display_dither == 'floyd-steinberg':
            quantized_image = resized_image.quantize(dither=Image.Dither.FLOYDSTEINBERG, palette=pal_image).convert('RGB')
        else:  # 'none'
            quantized_image = resized_image.quantize(dither=Image.Dither.NONE, palette=pal_image).convert('RGB')

        base = os.path.splitext(os.path.basename(input_filename))[0]
        output_basename = f"{base}_{detected_orientation}_{display_mode}_output.bmp"
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
    display_dither = args.dither

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

