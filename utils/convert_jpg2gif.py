from PIL import Image
import glob
import os

# 输入和输出路径
src_dir = "/homes/zwanglg/wzxhome/PISA/eval_data/result"
dst_path = os.path.join(src_dir, "output.gif")

# 按顺序读取所有 jpg 文件
frame_files = sorted(glob.glob(os.path.join(src_dir, "output_*.jpg")))

# 打开所有帧
frames = [Image.open(f) for f in frame_files]

# 保存为 gif
frames[0].save(
    dst_path,
    save_all=True,
    append_images=frames[1:],  # 后续帧
    duration=50,               # 每帧显示 50 毫秒 (20 fps 左右)
    loop=0                     # 无限循环
)

print(f"GIF has been saved: {dst_path}")
