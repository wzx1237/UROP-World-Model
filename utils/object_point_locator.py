from typing import Tuple, Optional, List
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

def _pick_point_from_bbox(
    bbox_xyxy: Tuple[float, float, float, float],
    mode: str = "center"
) -> Tuple[int, int]:
    """
    bbox_xyxy: (x1, y1, x2, y2) in pixel coords
    mode:
      - "center": bbox中心点
      - "topleft": 左上角
      - "top": 上边中点
      - "bottom": 下边中点
      - "left": 左边中点
      - "right": 右边中点
      - "random-ish": 偏上方一点（有时更像“指向物体”而不是中心）
    """
    x1, y1, x2, y2 = bbox_xyxy
    if mode == "center":
        x, y = (x1 + x2) / 2, (y1 + y2) / 2
    elif mode == "topleft":
        x, y = x1, y1
    elif mode == "top":
        x, y = (x1 + x2) / 2, y1
    elif mode == "bottom":
        x, y = (x1 + x2) / 2, y2
    elif mode == "left":
        x, y = x1, (y1 + y2) / 2
    elif mode == "right":
        x, y = x2, (y1 + y2) / 2
    elif mode == "random-ish":
        # 偏上 30% 的位置，避免某些物体中心落在空洞处（比如甜甜圈/环形）
        x = (x1 + x2) / 2
        y = y1 + 0.30 * (y2 - y1)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return int(round(x)), int(round(y))


@torch.inference_mode()
def locate_object_point(
    image: Image.Image,
    target_name: str,
    box_threshold: float = 0.25,
    text_threshold: float = 0.25,
    device: Optional[str] = None,
    point_mode: str = "center",
) -> Tuple[int, int]:
    """
    输入:
      - image: PIL.Image
      - target_name: 目标物体名字（英文效果通常更好；中文也可试）
    输出:
      - (x, y): 一个像素点，表示目标物体位置

    说明:
      - 如果检测到多个同名目标，默认取置信度最高的那个 bbox。
    """

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    model_id = "IDEA-Research/grounding-dino-base"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)

    # GroundingDINO对 prompt 习惯用英文短语；你也可以传 "a photo of {target_name}"
    text_prompt = target_name

    inputs = processor(images=image, text=text_prompt, return_tensors="pt").to(device)
    outputs = model(**inputs)

    # 把模型输出的归一化框还原到像素坐标
    target_sizes = torch.tensor([image.size[::-1]], device=device)  # (h, w)
    results = processor.post_process_grounded_object_detection(
        outputs=outputs,
        # inputs.input_ids, # I do not support this argument
        target_sizes=target_sizes,
        box_threshold=box_threshold,
        text_threshold=text_threshold,
    )

    # results 是长度为 batch 的 list，这里 batch=1
    r = results[0]
    boxes = r["boxes"]      # (N,4) xyxy in pixels
    scores = r["scores"]    # (N,)
    labels = r["labels"]    # (N,) 文本片段

    if boxes.numel() == 0:
        raise RuntimeError(
            f"no such target: {target_name}. "
            f"you can try to lower box_threshold/text_threshold, or change to more precise description"
        )

    # 取置信度最高的框
    best_idx = int(torch.argmax(scores).item())
    x1, y1, x2, y2 = boxes[best_idx].tolist()

    # 输出一个点
    return _pick_point_from_bbox((x1, y1, x2, y2), mode=point_mode)


if __name__ == "__main__":
    INPUT_DIR = r"/homes/zwanglg/wzxhome/PISA/eval_data/01/rgba_00000.jpg"
    img = Image.open(INPUT_DIR).convert("RGB")
    target = "shoe"  # 例如: "person", "dog", "traffic light", "bottle", ...
    x, y = locate_object_point(img, target, point_mode="random-ish")
    print((x, y))

# run in one line:
# python object_point_locator.py