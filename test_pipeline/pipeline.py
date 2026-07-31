#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi"}


def run_in_conda(
    command: str,
    cwd: Path,
    conda_env: str | None,
    dry_run: bool = False,
) -> None:
    if conda_env:
        wrapped_command = (
            'source "$(conda info --base)/etc/profile.d/conda.sh" && '
            f"conda activate {shlex.quote(conda_env)} && {command}"
        )
    else:
        wrapped_command = command

    full_command = ["bash", "-lc", wrapped_command]
    print(f"[RUN] cwd={cwd} env={conda_env or 'system'} cmd={command}")
    if dry_run:
        return
    subprocess.run(full_command, cwd=str(cwd), check=True)


def list_files(root: Path, suffixes: Iterable[str]) -> list[Path]:
    suffix_set = {s.lower() for s in suffixes}
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in suffix_set]


def copy_files(files: Sequence[Path], dst_dir: Path) -> list[Path]:
    copied = []
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        dst = dst_dir / src.name
        if dst.exists():
            stem = src.stem
            timestamp = int(time.time())
            dst = dst_dir / f"{stem}_{timestamp}{src.suffix}"
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def maybe_convert_frames_to_mp4(frames_dir: Path, output_path: Path, fps: int, dry_run: bool = False) -> bool:
    if not frames_dir.exists():
        return False
    jpg_frames = sorted(frames_dir.glob("*.jpg"))
    png_frames = sorted(frames_dir.glob("*.png"))
    frame_glob = None
    if jpg_frames:
        frame_glob = "*.jpg"
    elif png_frames:
        frame_glob = "*.png"
    if frame_glob is None:
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_cmd = (
        f'ffmpeg -y -framerate {fps} -pattern_type glob -i "{frame_glob}" '
        f'-c:v libx264 -pix_fmt yuv420p "{output_path}"'
    )
    run_in_conda(ffmpeg_cmd, cwd=frames_dir, conda_env=None, dry_run=dry_run)
    return True


def render_template(command: str, **kwargs: str) -> str:
    return command.format(**kwargs)


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    default_repo_root = script_dir.parent

    parser = argparse.ArgumentParser(description="Picture+Text -> Video pipeline (PhysX-Anything + MoReGen)")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--inputs-dir", type=Path)
    parser.add_argument("--meshes-dir", type=Path)
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--physx-dir", type=Path)
    parser.add_argument("--moregen-dir", type=Path)
    parser.add_argument("--prompts-file", type=Path, help="Text prompts file for MoReGen (typically MoReGen/prompts.txt)")
    parser.add_argument("--physx-env", default="physx-anything")
    parser.add_argument("--moregen-env", default="MoReGen")
    parser.add_argument("--physx-basepath", type=Path, help="PhysX output basepath that contains generated URDF files")
    parser.add_argument("--moregen-output-frames-dir", type=Path, help="MoReGen frame output dir")
    parser.add_argument("--moregen-output-video", type=Path, help="Known MoReGen output video path (optional)")
    parser.add_argument("--fps", type=int, default=16)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-physx", action="store_true")
    parser.add_argument("--skip-moregen", action="store_true")
    parser.add_argument(
        "--moregen-command",
        action="append",
        default=[],
        help=(
            "MoReGen command template (repeatable). "
            "Available placeholders: {moregen_dir},{meshes_dir},{results_dir},{prompts_file},{inputs_dir}"
        ),
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    inputs_dir = (args.inputs_dir or (repo_root / "inputs")).resolve()
    meshes_dir = (args.meshes_dir or (repo_root / "meshes")).resolve()
    results_dir = (args.results_dir or (repo_root / "results")).resolve()
    physx_dir = (args.physx_dir or (repo_root / "PhysX-Anything")).resolve()
    moregen_dir = (args.moregen_dir or (repo_root / "MoReGen")).resolve()
    prompts_file = (args.prompts_file or (moregen_dir / "prompts.txt")).resolve()
    physx_basepath = (args.physx_basepath or (physx_dir / "test_demo")).resolve()
    moregen_output_frames_dir = (args.moregen_output_frames_dir or (moregen_dir / "output_frames")).resolve()

    inputs_dir.mkdir(parents=True, exist_ok=True)
    meshes_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    png_files = sorted(inputs_dir.glob("*.png"))
    if not png_files:
        raise FileNotFoundError(f"No input png files found in: {inputs_dir}")
    if not prompts_file.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

    started_at = time.time()

    if not args.skip_physx:
        physx_commands = [
            (
                "python 1_vlm_demo.py --demo_path {inputs_dir} "
                "--save_part_ply True --remove_bg False --ckpt {physx_ckpt}"
            ),
            "python 2_decoder.py",
            "python 3_split.py",
            "python 4_simready_gen.py --voxel_define 32 --basepath {physx_basepath} --process 0 --fixed_base 0 --deformable 0",
        ]
        for command in physx_commands:
            rendered = render_template(
                command,
                inputs_dir=str(inputs_dir),
                physx_ckpt=str((physx_dir / "pretrain" / "vlm").resolve()),
                physx_basepath=str(physx_basepath),
            )
            run_in_conda(rendered, cwd=physx_dir, conda_env=args.physx_env, dry_run=args.dry_run)

    mesh_files = list_files(physx_basepath, [".urdf"])
    if not mesh_files:
        raise FileNotFoundError(f"No URDF meshes found in: {physx_basepath}")
    copied_meshes = copy_files(mesh_files, meshes_dir)
    print(f"[OK] Copied {len(copied_meshes)} mesh(es) to: {meshes_dir}")

    if not args.skip_moregen:
        moregen_commands = list(args.moregen_command)
        if not moregen_commands:
            moregen_commands = [
                (
                    "python demo.py --mesh_dir {meshes_dir} --prompt_file {prompts_file} "
                    "--output_frames_dir {moregen_output_frames_dir}"
                )
            ]
        for command in moregen_commands:
            rendered = render_template(
                command,
                moregen_dir=str(moregen_dir),
                meshes_dir=str(meshes_dir),
                results_dir=str(results_dir),
                prompts_file=str(prompts_file),
                inputs_dir=str(inputs_dir),
                moregen_output_frames_dir=str(moregen_output_frames_dir),
            )
            run_in_conda(rendered, cwd=moregen_dir, conda_env=args.moregen_env, dry_run=args.dry_run)

    candidate_videos = [
        p for p in list_files(moregen_dir, VIDEO_EXTENSIONS) if p.stat().st_mtime >= started_at
    ]
    copied_videos = copy_files(candidate_videos, results_dir) if candidate_videos else []

    if args.moregen_output_video:
        known_video = args.moregen_output_video.resolve()
        if known_video.exists():
            copied_videos.extend(copy_files([known_video], results_dir))

    if not copied_videos:
        fallback_mp4 = results_dir / "output.mp4"
        converted = maybe_convert_frames_to_mp4(
            frames_dir=moregen_output_frames_dir,
            output_path=fallback_mp4,
            fps=args.fps,
            dry_run=args.dry_run,
        )
        if converted:
            copied_videos = [fallback_mp4]

    if copied_videos:
        print("[OK] Result video(s):")
        for video in copied_videos:
            print(f"  - {video}")
    else:
        print("[WARN] No video detected or converted. Please verify your MoReGen command/output paths.")

    print("[DONE] Pipeline finished.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Command failed with exit code {exc.returncode}.", file=sys.stderr)
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
