# test_pipeline

这个目录提供了一个可直接运行的 `Picture(text) -> Video(mp4)` pipeline 入口，按你的约束把代码全部放在 `test_pipeline` 下。

## 文件

- `pipeline.py`：主流程脚本  
- `run_pipeline.sh`：Linux/bash 启动脚本

## 默认约定目录（都在仓库根目录下）

- 输入图片：`/home/runner/work/UROP-World-Model/UROP-World-Model/inputs`（`.png`）
- 网格输出：`/home/runner/work/UROP-World-Model/UROP-World-Model/meshes`（`.urdf`）
- 最终视频：`/home/runner/work/UROP-World-Model/UROP-World-Model/results`（`.mp4`）
- PhysX-Anything：`/home/runner/work/UROP-World-Model/UROP-World-Model/PhysX-Anything`
- MoReGen：`/home/runner/work/UROP-World-Model/UROP-World-Model/MoReGen`
- 文本提示：`MoReGen/prompts.txt`

## 默认 PhysX 阶段命令

脚本会在 `physx-anything` 环境中按顺序执行：

1. `python 1_vlm_demo.py --demo_path <inputs_dir> --save_part_ply True --remove_bg False --ckpt <PhysX-Anything/pretrain/vlm>`
2. `python 2_decoder.py`
3. `python 3_split.py`
4. `python 4_simready_gen.py --voxel_define 32 --basepath <PhysX-Anything/test_demo> --process 0 --fixed_base 0 --deformable 0`

并自动把 `test_demo` 下生成的 `.urdf` 复制到 `meshes/`。

## 默认 MoReGen 阶段

脚本会在 `MoReGen` 环境中执行默认命令：

`python demo.py --mesh_dir <meshes_dir> --prompt_file <prompts_file> --output_frames_dir <MoReGen/output_frames>`

如果你的 MoReGen 命令不同，可用 `--moregen-command` 覆盖（支持重复传入多条命令）。

## 运行示例（Linux/bash）

```bash
cd /home/runner/work/UROP-World-Model/UROP-World-Model
bash /home/runner/work/UROP-World-Model/UROP-World-Model/test_pipeline/run_pipeline.sh
```

自定义 MoReGen 命令示例：

```bash
bash /home/runner/work/UROP-World-Model/UROP-World-Model/test_pipeline/run_pipeline.sh \
  --moregen-command "python your_moregen_entry.py --mesh_dir {meshes_dir} --prompt_file {prompts_file} --out {results_dir}"
```

## 常用参数

- `--physx-env`（默认 `physx-anything`）
- `--moregen-env`（默认 `MoReGen`）
- `--inputs-dir` / `--meshes-dir` / `--results-dir`
- `--physx-dir` / `--moregen-dir`
- `--prompts-file`
- `--moregen-output-frames-dir`
- `--moregen-output-video`
- `--fps`
- `--skip-physx` / `--skip-moregen`
- `--dry-run`

## 输出行为

- 优先收集 MoReGen 新生成的视频文件（`mp4/mkv/mov/avi`）到 `results/`。
- 若未检测到视频，会尝试把 `output_frames` 中的 jpg/png 用 `ffmpeg` 合成为 `results/output.mp4`。
