import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path("wooden_man.xml")
data = mujoco.MjData(model)

# 启用可视化窗口
with mujoco.viewer.launch_passive(model, data) as viewer:
  while viewer.is_running():
    mujoco.mj_step(model, data)   # 仿真一步
    viewer.sync()                 # 刷新画面
