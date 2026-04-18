from PIL import Image
import os

BASE = r"/homes/zwanglg/wzxhome/PhysX-Anything/demo"
inp  = "shoe.png"
out  = "shoe_1024.png"
size = 1024
target_fill = 0.70  # 鞋子占画面宽/高的比例，0.7~0.9 都行

im = Image.open(os.path.join(BASE, inp)).convert("RGBA")

# 按 alpha 裁掉多余透明边
alpha = im.split()[-1]
bbox = alpha.getbbox()
im = im.crop(bbox) if bbox else im

w, h = im.size
scale = int(size * target_fill / max(w, h))
new_w = max(1, int(w * scale))
new_h = max(1, int(h * scale))
im = im.resize((new_w, new_h), resample=Image.LANCZOS)

# 放到 1024x1024 透明画布中心
canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
x = (size - new_w) // 2
y = (size - new_h) // 2
canvas.paste(im, (x, y), im)

canvas.save(os.path.join(BASE, out))
print("saved:", os.path.join(BASE, out), "object_size:", (new_w, new_h))
