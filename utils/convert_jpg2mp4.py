import cv2
import glob
import os

IMAGE_PATH = "/homes/zwanglg/wzxhome/PISA/eval_data/01"

# for 01, file name: rgba_*.jpg
# mydemo, file name: output_*.jpg
frame_files = sorted(glob.glob(os.path.join(IMAGE_PATH, "rgba_*.jpg")))
frame = cv2.imread(frame_files[0])
height, width, _ = frame.shape

out = cv2.VideoWriter(os.path.join(IMAGE_PATH, "output.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 16, (width, height))

for f in frame_files:
    img = cv2.imread(f)
    out.write(img)

out.release()
print("Saved output.mp4 to:", os.path.join(IMAGE_PATH, "output.mp4"))
