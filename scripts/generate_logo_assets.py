#!/usr/bin/env python3
"""
SURE SAVINGS Logo Asset Generator
Extracts and generates production-ready logo and favicon assets
from the uploaded visual reference image.
"""

import os
from PIL import Image, ImageFilter, ImageOps

SRC_PATH = "/Users/satyabratadas/.gemini/antigravity-ide/brain/1e2db605-7054-45e3-a81e-a7a30ec71e25/.user_uploaded/media_1789460093969.jpg"
OUTPUT_DIR = "/Users/satyabratadas/Documents/SURE SAVINGS/assets/images"
ROOT_DIR = "/Users/satyabratadas/Documents/SURE SAVINGS"

os.makedirs(OUTPUT_DIR, exist_ok=True)

orig = Image.open(SRC_PATH).convert("RGB")
w, h = orig.size
orig_pix = orig.load()

# -------------------------------------------------------------
# 1. High-Precision De-fringed Alpha Matte for Central S-Mark
# -------------------------------------------------------------
out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
out_pix = out.load()

wr, wg, wb = 254.0, 254.0, 254.0

for y in range(h):
    for x in range(w):
        # Outer boundary check for the logo mark
        if x < 205 or x > 815 or y < 135 or y > 860:
            continue
        
        r, g, b = orig_pix[x, y]
        br = (r + g + b) / 3.0
        
        # Color difference from white
        diff_r = wr - r
        diff_g = wg - g
        diff_b = wb - b
        
        dist = max(diff_g, diff_b) if r > g and r > b else max(diff_r, diff_g, diff_b)
        
        # Bottom ambient shadow under navy ribbon cutoff:
        # The navy ribbon has br < 80. Shadow pixels have br > 110.
        if y > 830 and br > 105 and (max(r, g, b) - min(r, g, b) < 30 or r > 140):
            continue
            
        # Top loop inner negative space (white hole)
        if 320 <= y <= 370 and 385 <= x <= 485:
            if r > 230 and g > 225 and b > 225:
                continue

        # Area between three bars and lower ribbon
        if 700 <= y <= 735 and 430 <= x <= 630:
            if r > 230 and g > 225 and b > 225:
                continue
                
        # Inner gaps between the bars
        # Gap between Bar 1 & Bar 2: x ~ 492..512
        if 590 <= y <= 720 and 492 <= x <= 512:
            if r > 225 and g > 220 and b > 220:
                continue
        # Gap between Bar 2 & Bar 3: x ~ 558..576
        if 570 <= y <= 720 and 558 <= x <= 576:
            if r > 225 and g > 220 and b > 220:
                continue
                
        # Space above the three bars under the diagonal ribbon
        if 555 <= y <= 610 and 445 <= x <= 625:
            if r > 225 and g > 220 and b > 220:
                continue
                
        # Space right of bar 3
        if 570 <= y <= 720 and 618 <= x <= 680:
            if r > 225 and g > 220 and b > 220:
                continue
                
        # Space left of bar 1
        if 640 <= y <= 720 and 388 <= x <= 445:
            if r > 225 and g > 220 and b > 220:
                continue

        # Alpha calculation
        if dist > 35:
            alpha = min(1.0, max(0.0, (dist - 15) / 30.0))
            a_byte = int(alpha * 255)
            
            # De-fringe edge pixels against white background
            if 0.05 < alpha < 0.99:
                fr = min(255, max(0, int((r - (1 - alpha) * wr) / alpha)))
                fg = min(255, max(0, int((g - (1 - alpha) * wg) / alpha)))
                fb = min(255, max(0, int((b - (1 - alpha) * wb) / alpha)))
                out_pix[x, y] = (fr, fg, fb, a_byte)
            elif alpha >= 0.99:
                out_pix[x, y] = (r, g, b, 255)

# Tight crop to logo bounds
bbox = out.getbbox()
logo_cropped = out.crop(bbox)
cw, ch = logo_cropped.size

# Place onto centered 1024x1024 square canvas with proportional padding (7% margin)
target_size = 1024
padding = int(target_size * 0.07)
avail_size = target_size - 2 * padding
scale = avail_size / max(cw, ch)
new_cw = int(cw * scale)
new_ch = int(ch * scale)

logo_scaled = logo_cropped.resize((new_cw, new_ch), Image.Resampling.LANCZOS)
master_logo = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
offset_x = (target_size - new_cw) // 2
offset_y = (target_size - new_ch) // 2
master_logo.paste(logo_scaled, (offset_x, offset_y), logo_scaled)

# Save Master Logo PNG & WebP
master_png_path = os.path.join(OUTPUT_DIR, "sure-savings-logo.png")
master_webp_path = os.path.join(OUTPUT_DIR, "sure-savings-logo.webp")
master_logo.save(master_png_path, "PNG", optimize=True)
master_logo.save(master_webp_path, "WEBP", quality=95)
print(f"Saved: {master_png_path} ({master_logo.size})")
print(f"Saved: {master_webp_path}")

# -------------------------------------------------------------
# 2. App Icon / Squircle Tile Asset
# -------------------------------------------------------------
# Extract the rounded squircle tile from the original image (x: 108..916, y: 88..896)
squircle_box = (108, 88, 916, 896)
tile_cropped = orig.crop(squircle_box)
tw, th = tile_cropped.size

# Create a rounded squircle mask for the tile
tile_mask = Image.new("L", (tw, th), 0)
from PIL import ImageDraw
draw = ImageDraw.Draw(tile_mask)
# Apple squircle radius is ~22.5% of dimension
corner_radius = int(tw * 0.225)
draw.rounded_rectangle([(0, 0), (tw - 1, th - 1)], radius=corner_radius, fill=255)

tile_rgba = tile_cropped.convert("RGBA")
tile_rgba.putalpha(tile_mask)
tile_1024 = tile_rgba.resize((1024, 1024), Image.Resampling.LANCZOS)

icon_path = os.path.join(OUTPUT_DIR, "sure-savings-icon.png")
tile_1024.save(icon_path, "PNG", optimize=True)
print(f"Saved: {icon_path}")

# Apple Touch Icon (180x180)
apple_touch_path = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")
apple_touch_img = tile_1024.resize((180, 180), Image.Resampling.LANCZOS)
apple_touch_img.save(apple_touch_path, "PNG", optimize=True)
print(f"Saved: {apple_touch_path}")

# Also save apple-touch-icon in root directory for standard web crawlers
apple_touch_root = os.path.join(ROOT_DIR, "apple-touch-icon.png")
apple_touch_img.save(apple_touch_root, "PNG", optimize=True)

# -------------------------------------------------------------
# 3. Favicon Assets (16x16, 32x32, 48x48, .ico)
# -------------------------------------------------------------
# For small favicons (16x16, 32x32), use the central S-mark with a tighter crop
# so it remains ultra-clear and punchy in browser tabs
fav_margin = int(target_size * 0.03)
fav_avail = target_size - 2 * fav_margin
fav_scale = fav_avail / max(cw, ch)
fav_cw = int(cw * fav_scale)
fav_ch = int(ch * fav_scale)
fav_scaled = logo_cropped.resize((fav_cw, fav_ch), Image.Resampling.LANCZOS)

fav_base = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
fav_ox = (target_size - fav_cw) // 2
fav_oy = (target_size - fav_ch) // 2
fav_base.paste(fav_scaled, (fav_ox, fav_oy), fav_scaled)

fav_16 = fav_base.resize((16, 16), Image.Resampling.LANCZOS)
fav_32 = fav_base.resize((32, 32), Image.Resampling.LANCZOS)
fav_48 = fav_base.resize((48, 48), Image.Resampling.LANCZOS)

# Save PNG favicons
fav_16_path = os.path.join(OUTPUT_DIR, "favicon-16x16.png")
fav_32_path = os.path.join(OUTPUT_DIR, "favicon-32x32.png")
fav_48_path = os.path.join(OUTPUT_DIR, "favicon-48x48.png")
fav_16.save(fav_16_path, "PNG", optimize=True)
fav_32.save(fav_32_path, "PNG", optimize=True)
fav_48.save(fav_48_path, "PNG", optimize=True)
print(f"Saved: {fav_16_path}, {fav_32_path}, {fav_48_path}")

# Multi-resolution ICO
ico_root_path = os.path.join(ROOT_DIR, "favicon.ico")
ico_assets_path = os.path.join(OUTPUT_DIR, "favicon.ico")
fav_base.save(ico_root_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
fav_base.save(ico_assets_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
print(f"Saved: {ico_root_path}")
print(f"Saved: {ico_assets_path}")

# -------------------------------------------------------------
# 4. SVG Assets (Embeds lossless optimized high-res logo data)
# -------------------------------------------------------------
import base64
with open(master_png_path, "rb") as f:
    b64_png = base64.b64encode(f.read()).decode("ascii")

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="100%" height="100%">
  <title>SURE SAVINGS Logo</title>
  <desc>SURE SAVINGS smart liquidity intelligence logo mark</desc>
  <image href="data:image/png;base64,{b64_png}" x="0" y="0" width="1024" height="1024" preserveAspectRatio="xMidYMid meet"/>
</svg>
'''

svg_path = os.path.join(OUTPUT_DIR, "sure-savings-logo.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"Saved: {svg_path}")

# Also favicon.svg
fav_svg_path = os.path.join(OUTPUT_DIR, "favicon.svg")
with open(fav_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"Saved: {fav_svg_path}")

print("All SURE SAVINGS logo assets successfully generated!")
