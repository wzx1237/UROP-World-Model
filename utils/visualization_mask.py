import numpy as np
import glob
from PIL import Image, ImageDraw
import os

# 注意事项：
# 1. 每次生成新的visualization时，先查看BASE_DIR是不是正确的
# 2. frame_files的filename有没有更新
# 3. 输出的gif名字是不是会覆盖之前的

# 0. load base dir
BASE_DIR = "/homes/zwanglg/wzxhome/PISA/eval_data/01/"

# 1. 读取 mask.npz
mask_data = np.load(os.path.join(BASE_DIR, "mask.npz"))
mask_array = mask_data["mask"]   # shape: [V, N, H, W]

# 2. 读取对应的 jpg 帧
frame_files = sorted(glob.glob(os.path.join(BASE_DIR, "rgba_*.jpg")))

# 3. 输出 gif 路径
DST_GIF = "/homes/zwanglg/wzxhome/PISA/eval_data/vis_mask/paper_mask.gif"

frames_out = []

# 4. 设置一个flag来决定我们是想看到mask和原图的叠加还是只有mask
mask_only = True

# 5. 每个物体用不同颜色
colors = [(255,0,0,100), (0,255,0,100), (0,0,255,100), (255,255,0,100)]

if mask_only == False:
# 6. 遍历每一帧，叠加掩码
    for v, f in enumerate(frame_files):
        img = Image.open(f).convert("RGB")
        overlay = Image.new("RGBA", img.size, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)

        for n in range(mask_array.shape[1]):
            mask = mask_array[v, n]
            if mask.sum() == 0:
                continue
            # 把掩码转成坐标点
            ys, xs = np.where(mask > 0)
            for (x,y) in zip(xs, ys):
                draw.point((x,y), fill=colors[n % len(colors)])

        # 合成原图和掩码
        img_out = Image.alpha_composite(img.convert("RGBA"), overlay)
        frames_out.append(img_out.convert("RGB"))
else:
    mask_color = [
        (255,0,0), (0,255,0), (0,0,255), (255,255,0),
        (255,0,255), (0,255,255), (128,128,255), (255,128,128)
    ]
    for v in range(mask_array.shape[0]):
        H, W = mask_array.shape[2], mask_array.shape[3]
        canvas = np.zeros((H, W, 3), dtype=np.uint8)

        for n in range(mask_array.shape[1]):
            mask = mask_array[v, n]
            if mask.sum() == 0:
                continue
            color = mask_color[n % len(colors)]
            canvas[mask > 0] = color

        frames_out.append(Image.fromarray(canvas))

# 5. 保存为 gif
frames_out[0].save(
    DST_GIF,
    save_all=True,
    append_images=frames_out[1:],
    duration=100,   # 每帧 100ms ≈ 10fps
    loop=0
)

print(f"可视化 GIF 已保存到: {DST_GIF}")
