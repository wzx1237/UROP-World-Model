import mujoco
import mujoco.viewer
import numpy as np
import time

# 加载模型和数据
model = mujoco.MjModel.from_xml_path("wooden_man.xml")
data = mujoco.MjData(model)

# 打开交互式 viewer
with mujoco.viewer.launch_passive(model, data) as viewer:
    t0 = time.time()
    while viewer.is_running():
        # 当前时间
        t = time.time() - t0

        # 控制信号：让左臂关节来回摆动
        # sin 波动在 [-0.5, 0.5] 之间
        data.ctrl[model.actuator("left_arm_motor").id] = 0.5 * np.sin(2 * np.pi * 0.5 * t)

        # 前进一步仿真
        mujoco.mj_step(model, data)

        # 更新 viewer
        viewer.sync()
