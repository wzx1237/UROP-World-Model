from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
import numpy as np
from PIL import Image
import glob
import os

# 0. load base
BASE_DIR = "/homes/zwanglg/wzxhome/PISA/eval_data/01/"

# 1. 加载模型
checkpoint = "sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
sam_model = build_sam2(model_cfg, checkpoint)

mask_generator = SAM2AutomaticMaskGenerator(sam_model)

# 2. 输入帧目录
frame_files = sorted(glob.glob(os.path.join(BASE_DIR, "rgba_*.jpg")))
all_masks = []

# 3. 遍历每一帧，自动生成掩码
for f in frame_files:
    image = np.array(Image.open(f))
    masks = mask_generator.generate(image)  # 自动分割，不需要 points
    frame_masks = [m["segmentation"].astype(np.uint8) for m in masks]
    all_masks.append(frame_masks)

# 4. 整理成 PisaBench 格式 [V, N, H, W]
max_objects = max(len(m) for m in all_masks)
V = len(all_masks)
H, W = all_masks[0][0].shape
mask_array = np.zeros((V, max_objects, H, W), dtype=np.uint8)

for v, frame_masks in enumerate(all_masks):
    for n, m in enumerate(frame_masks):
        mask_array[v, n] = m

# 5. 保存为 mask.npz
np.savez_compressed(os.path.join(BASE_DIR, "mask_new.npz"), mask=mask_array)
print("Saved mask_new.npz")



# run the code:
# python ./data_processing/my_mask.py