import os
import subprocess
import time

import socket
import struct
import json

VIS_HOST = '127.0.0.1'  # Server address
VIS_PORT = 23457        # Server port

CODE_HOST = '127.0.0.1'
CODE_PORT = 10586       # Server port

MANIM_EXECUTABLE = r"/homes/zwanglg/wzxhome/miniconda3/envs/MoReGen/bin/manim"  # Path to Manim executable
PYBULLET_EXECUTABLE = r"/homes/zwanglg/wzxhome/miniconda3/envs/MoReGen/bin/python"  # Use python to run pybullet scripts

BASE_DIR = r"/homes/zwanglg/wzxhome/MoReGen/result/" + time.strftime("%Y%m%d-%H%M%S")

ITER_LOOP = 2
PROMPT_LOC = r"/homes/zwanglg/wzxhome/MoReGen/prompts.txt"
PROMPT_JSON = r"/homes/zwanglg/wzxhome/MoReGen/prompts_json.json"

# log directory:
LOG = r"/homes/zwanglg/wzxhome/MoReGen/log"
VIS_LOG = r"/homes/zwanglg/wzxhome/MoReGen/VisualFeedback_log"

# Engine toggle
IS_MANIM = False


def load_prompts():
    with open(PROMPT_LOC, 'r') as f:
        prompts = f.read()

    with open(PROMPT_JSON, 'r') as f:
        prompt_json = json.load(f)

    return prompts.strip(), prompt_json


def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


# init_code: 'gemini', 'qwen' or None
def send_code_request(prompt, prompt_json, code, fix_code, init_code, client='manim'):
    intent = 'fix_code' if fix_code else 'init_code'
    llm = init_code if init_code else 'qwen'
    req = {
        'prompt_a': prompt,
        'prompt_b': prompt_json,
        'video_path': None,
        'code': code,
        'intent': intent,
        'llm': llm,
        'client': client,
    }
    data = json.dumps(req).encode('utf-8')

    with open(LOG, 'a') as f:
        f.write(req['intent'] + " " + req['llm'] + "\n")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((CODE_HOST, CODE_PORT))
        s.sendall(struct.pack('>I', len(data)))
        s.sendall(data)

        raw_msglen = recvall(s, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        response = recvall(s, msglen)
        return json.loads(response.decode('utf-8'))


# returns is_success, result_path (mp4 path or frames dir), code_path
def render_videos(i):
    tmpdir = BASE_DIR
    os.makedirs(tmpdir, exist_ok=True)
    script_path = os.path.join(tmpdir, f"scene_{i:04d}.py")

    try:
        if IS_MANIM:
            result = subprocess.run(
                [MANIM_EXECUTABLE, script_path],
                capture_output=True,
                text=True,
                cwd=tmpdir,
            )
        else:
            frames_dir = os.path.join(tmpdir, f"frames_{i:04d}")
            os.makedirs(frames_dir, exist_ok=True)
            env = dict(os.environ)
            env["OUTPUT_FRAMES_DIR"] = frames_dir
            result = subprocess.run(
                [PYBULLET_EXECUTABLE, script_path],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                env=env,
            )

        if result.returncode != 0:
            err_msg = result.stderr or "Unknown error"
            print(f"Execution failed: {err_msg}")
            return False, err_msg, script_path

        out = result.stdout or ""

        if IS_MANIM:
            file_loc = out.split('File ready at')[-1].split('INFO')[0].split('[')[0]
            file_loc = file_loc.replace('\n', '').replace(' ', '').replace("'", "").strip()

            # Legacy mp4 rename logic (kept as comment):
            # old_file_loc = file_loc
            # prior = file_loc.split('\\')[:-1]
            # file_loc = file_loc.split('\\')[-1].split(".")[0] + f"_{i:04d}.mp4"
            # prior.append(file_loc)
            # file_loc = '\\'.join(prior)
            # os.rename(old_file_loc, file_loc)

            print(f"Extracted file location: {file_loc}")
            return True, file_loc.replace('\\', '/'), script_path

        # PyBullet headless: return frames directory; generated script should print the same.
        frames_dir = os.environ.get("OUTPUT_FRAMES_DIR")
        if "Frames ready at:" in out:
            frames_dir = out.split("Frames ready at:")[-1].strip().splitlines()[0]
        if not frames_dir:
            frames_dir = os.path.join(tmpdir, f"frames_{i:04d}")
        print(f"Frames ready at: {frames_dir}")
        return True, frames_dir, script_path

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        return False, str(e), script_path


# returns the path to the updated script
def update_scripts(new_code, i):
    new_code = new_code.split("```python")[-1].split("```")[0] if len(new_code.split("```")) > 1 else new_code
    tmpdir = BASE_DIR
    os.makedirs(tmpdir, exist_ok=True)
    script_path = os.path.join(tmpdir, f"scene_{i:04d}.py")
    with open(script_path, 'w') as f:
        f.write(new_code)
    return script_path


def vis_feedback(video_path_or_frames_path):
    prompt = "Please describe what is not aligned with physics rules in the video."

    # Legacy server accepted {'prompt', 'video_path'}.
    # Newer server prefers {'feedback_prompt', 'frames_path'} for frame sequences.
    if IS_MANIM:
        payload = {
            'purpose': 'feedback',
            'prompt': prompt,
            'video_path': video_path_or_frames_path,
        }
    else:
        payload = {
            'purpose': 'feedback',
            'feedback_prompt': prompt,
            'frames_path': video_path_or_frames_path,
        }

    req = json.dumps(payload).encode('utf-8')
    msg = struct.pack('>I', len(req)) + req
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((VIS_HOST, VIS_PORT))
        s.sendall(msg)

        raw_msglen = recvall(s, 4)
        if not raw_msglen:
            print('No response from server')
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = recvall(s, msglen)
        if not data:
            print('No data received')
            return None

        with open(VIS_LOG, 'a') as f:
            f.write(f"Feedback for video/frames {video_path_or_frames_path}: " + data.decode('utf-8') + "\n")

        resp = json.loads(data.decode('utf-8'))
        return resp.get('visual_feedback') or resp.get('visual_feedback_physics')


if __name__ == "__main__":
    print("Starting Agent...")
    with open(LOG, 'w') as f:
        f.write("trials start at " + time.strftime("%Y%m%d-%H%M%S") + "\n")
    with open(VIS_LOG, 'w') as f:
        f.write("trail start at " + time.strftime("%Y%m%d-%H%M%S") + "\n")

    os.makedirs(BASE_DIR, exist_ok=True)
    prompts, prompt_json = load_prompts()
    prompt_json = json.dumps(prompt_json)
    prompt_json = "```json\n" + prompt_json + "\n```"

    print("starting construct feedback loop...")
    print("sleep for a while, waiting for other two program start")
    time.sleep(30)

    if IS_MANIM:
        code = send_code_request(prompts, None, None, fix_code=False, init_code='gpt', client='manim')
    else:
        code = send_code_request(prompts, None, None, fix_code=False, init_code='gpt', client='pybullet')

    print("sent code request successfully")

    update_scripts(code['code'], 0)
    for it in range(0, ITER_LOOP):
        print(f"--- Iteration {it} ---")
        is_success, result_path, script_path = render_videos(it)
        while not is_success:
            print("Rendering failed, requesting code fix...")
            with open(LOG, 'a') as f:
                f.write(result_path + '\n')

            if IS_MANIM:
                code = send_code_request(prompts, result_path, code['code'], fix_code=True, init_code='gpt', client='manim')
            else:
                code = send_code_request(prompts, result_path, code['code'], fix_code=True, init_code='gpt', client='pybullet')

            update_scripts(code['code'], it)
            is_success, result_path, script_path = render_videos(it)

        print(f"Render result at: {result_path}")
        vis_result = vis_feedback(result_path)
        print(f"Visual feedback: {vis_result}")
        # with open(VIS_LOG, 'a') as f:
            # f.write(vis_result + '\n')

        if IS_MANIM:
            code = send_code_request(prompts, vis_result[0], code['code'], fix_code=False, init_code='gpt', client='manim')
        else:
            code = send_code_request(prompts, vis_result[0], code['code'], fix_code=False, init_code='gpt', client='pybullet')

        update_scripts(code['code'], it + 1)


if False:
    """
    Legacy snapshot (the corrupted version right before rewrite):

import os
import subprocess
import time

import socket
import struct
import json

VIS_HOST = '127.0.0.1'  # Server address
VIS_PORT = 23456        # Server port
# CODE_HOST = 'zzzura.duckdns.org'  # Server address
CODE_HOST = 'localhost'
CODE_PORT = 10586        # Server port

MANIM_EXECUTABLE = r"/homes/zwanglg/wzxhome/miniconda3/envs/MoReGen/bin/manim"  # Path to Manim executable
PYBULLET_EXECUTABLE = r"/homes/zwanglg/wzxhome/miniconda3/envs/MoReGen/bin/python"
# path to python
# 由于pybullet没有CLI入口脚本，我们让 python 直接执行生成的脚本。

# add an agent flag
IS_MANIM = True

BASE_DIR = r"/homes/zwanglg/wzxhome/MoReGen/result/"+time.strftime("%Y%m%d-%H%M%S")
 
ITER_LOOP = 5
PROMPT_LOC = r"/homes/zwanglg/wzxhome/MoReGen/prompts"
PROMPT_JSON = r"/homes/zwanglg/wzxhome/MoReGen/prompts_json.json"

# log directory:
# for fix code log:
LOG = r"/homes/zwanglg/wzxhome/MoReGen/log"
# for visual feedback log:
VIS_LOG = r"/homes/zwanglg/wzxhome/MoReGen/VisualFeedback_log"

def load_prompts():
    with open(PROMPT_LOC, 'r') as f:
        prompts = f.read()
    
    with open(PROMPT_JSON, 'r') as f:
        prompt_json = json.load(f)

    return prompts.strip(), prompt_json

def recvall(sock, n):
    data = b''
    while len(data) < n:
    # script_path = os.path.join(tmpdir, f"scene_{iter:04d}.py")
    script_path = os.path.join(tmpdir, f"scene_{i:04d}.py")
        if not packet:
            return None
        data += packet
    return data

# init_code: 'gemini', 'qwen' or None
def send_code_request(prompt, prompt_json, code, fix_code, init_code, client='manim'):
    # Determine intent and llm to match run_coder.py handler protocol
    if fix_code:
        intent = 'fix_code'
            frames_dir = os.path.join(tmpdir, f"frames_{i:04d}")
            os.makedirs(frames_dir, exist_ok=True)
            env = dict(os.environ)
            env["OUTPUT_FRAMES_DIR"] = frames_dir
    else:
        intent = 'init_code'
    llm = init_code if init_code else 'qwen'
    req = {
                cwd=tmpdir,
                env=env,
        'prompt_b': prompt_json,
        'video_path': None,
        'code': code,
            if IS_MANIM:
                file_loc = out.split('File ready at')[-1].split('INFO')[0].split('[')[0].replace('\n','').replace(' ','').replace("\'", "").strip()
                # Extract file_loc from Manim output
                old_file_loc = file_loc
                prior = file_loc.split('\\')[:-1]
                file_loc = file_loc.split('\\')[-1].split(".")[0] + f"_{i:04d}.mp4"
                prior.append(file_loc)
                file_loc = '\\'.join(prior)
                os.rename(old_file_loc, file_loc)
                print(f"Extracted file location: {file_loc}")
                return True, file_loc.replace('\\', '/'), script_path
            else:
                # For PyBullet headless runs, we expect frames to be written to OUTPUT_FRAMES_DIR.
                # Optionally, generated script can print: "Frames ready at: <dir>".
                frames_dir = os.environ.get("OUTPUT_FRAMES_DIR")
                if "Frames ready at:" in out:
                    frames_dir = out.split("Frames ready at:")[-1].strip().splitlines()[0]
                if not frames_dir:
                    frames_dir = os.path.join(tmpdir, f"frames_{i:04d}")
                print(f"Frames ready at: {frames_dir}")
                return True, frames_dir, script_path

    """