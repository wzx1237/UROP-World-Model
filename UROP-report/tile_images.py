import os
import math
import argparse
from PIL import Image, ImageDraw, ImageFont

IMG_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")

def natural_key(s: str):
    # Sort like: img2.png < img10.png
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def list_images(input_dir: str):
    files = []
    for fn in os.listdir(input_dir):
        if fn.lower().endswith(IMG_EXTS):
            files.append(os.path.join(input_dir, fn))
    files.sort(key=lambda p: natural_key(os.path.basename(p)))
    return files

def load_font(font_size: int, font_path: str | None):
    if font_size <= 0:
        return None
    # Try a reasonable default
    try:
        if font_path:
            return ImageFont.truetype(font_path, font_size)
        # DejaVu is usually available in many environments; Overleaf isn't needed here anyway.
        return ImageFont.truetype("DejaVuSans.ttf", font_size)
    except Exception:
        return ImageFont.load_default()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True, help="Directory containing images")
    ap.add_argument("--output", default="mosaic.png", help="Output file path")
    ap.add_argument("--cols", type=int, default=8, help="Number of columns per row")
    ap.add_argument("--pad", type=int, default=10, help="Padding between tiles (pixels)")
    ap.add_argument("--bg", default="#ffffff", help="Background color, e.g. '#ffffff' or 'white'")
    ap.add_argument("--resize", default="", help="Resize each tile to WxH, e.g. '256x256'. Empty = no resize")
    ap.add_argument("--keep_aspect", action="store_true",
                    help="If resizing, keep aspect ratio by letterboxing (instead of stretching).")

    # Optional label on each tile
    ap.add_argument("--label", default="", help="Label text drawn at top-left of each tile (empty = none)")
    ap.add_argument("--label_height", type=int, default=0,
                    help="Extra top margin reserved for label per tile (pixels). 0 = auto if label is set.")
    ap.add_argument("--font_size", type=int, default=24, help="Label font size")
    ap.add_argument("--font_path", default="", help="Optional .ttf font path for label")
    ap.add_argument("--label_color", default="#000000", help="Label text color")
    args = ap.parse_args()

    paths = list_images(args.input_dir)
    if not paths:
        raise SystemExit(f"No images found in {args.input_dir}")

    # Parse resize
    target_w = target_h = None
    if args.resize:
        try:
            w, h = args.resize.lower().split("x")
            target_w, target_h = int(w), int(h)
        except Exception:
            raise SystemExit("--resize must look like '256x256'")

    # Load images
    imgs = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        if target_w and target_h:
            if args.keep_aspect:
                # Letterbox to target size
                im_ratio = im.width / im.height
                target_ratio = target_w / target_h
                if im_ratio > target_ratio:
                    new_w = target_w
                    new_h = int(target_w / im_ratio)
                else:
                    new_h = target_h
                    new_w = int(target_h * im_ratio)
                im_resized = im.resize((new_w, new_h), Image.LANCZOS)
                canvas = Image.new("RGB", (target_w, target_h), args.bg)
                off_x = (target_w - new_w) // 2
                off_y = (target_h - new_h) // 2
                canvas.paste(im_resized, (off_x, off_y))
                im = canvas
            else:
                im = im.resize((target_w, target_h), Image.LANCZOS)
        imgs.append(im)

    tile_w = imgs[0].width
    tile_h = imgs[0].height

    # Label handling
    font = load_font(args.font_size, args.font_path or None)
    label = args.label.strip()
    label_h = args.label_height
    if label and label_h == 0:
        # reserve a bit of space so label doesn't cover content too much
        label_h = int(args.font_size * 1.6)

    cols = max(1, args.cols)
    rows = math.ceil(len(imgs) / cols)

    out_w = cols * tile_w + (cols - 1) * args.pad
    out_h = rows * (tile_h + label_h) + (rows - 1) * args.pad

    out = Image.new("RGB", (out_w, out_h), args.bg)
    draw = ImageDraw.Draw(out)

    for idx, im in enumerate(imgs):
        r = idx // cols
        c = idx % cols
        x = c * (tile_w + args.pad)
        y = r * (tile_h + label_h + args.pad)

        # paste tile below the label area
        out.paste(im, (x, y + label_h))

        # draw label
        if label:
            # simple text at top-left of each tile cell
            draw.text((x + 5, y + 5), label, fill=args.label_color, font=font)

    out.save(args.output)
    print(f"[OK] Saved mosaic: {args.output}  ({len(imgs)} tiles, {rows}x{cols})")

if __name__ == "__main__":
    main()

# 横向拼一排, 假设有12张图
# python tile_images.py --input_dir ./results --cols 12 --pad 8 --bg "#ffffff" --output image.png

# 统一 resize，避免大小不一致
# python tile_images.py --input_dir ./results --cols 10 --resize 256x256 --output mosaic.png