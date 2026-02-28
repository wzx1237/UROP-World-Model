import time
import numpy as np
import mujoco
import mujoco.viewer


def main():
  model = mujoco.MjModel.from_xml_path("newtons_cradle_5_balls.xml")
  data = mujoco.MjData(model)

  # Use the named camera if present (0 is free camera; named cameras are after it).
  cam_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, "cam_front")
  with mujoco.viewer.launch_passive(model, data) as viewer:
    if cam_id != -1:
      viewer.cam.type = mujoco.mjtCamera.mjCAMERA_FIXED
      viewer.cam.fixedcamid = cam_id

  # Let contacts happen; Newton's cradle benefits from higher solver quality.
  model.opt.iterations = max(model.opt.iterations, 100)
  model.opt.ls_iterations = max(model.opt.ls_iterations, 20)

  # Add a small amount of global damping to gradually lose momentum (as described).
  # This is a simple way to model losses without complex string/air friction modeling.
  model.dof_damping[:] = np.maximum(model.dof_damping, 0.02)

  mujoco.mj_forward(model, data)

  # Simulation parameters
  sim_duration = 120.0  # seconds
  dt = model.opt.timestep
  steps = int(sim_duration / dt)

  with mujoco.viewer.launch_passive(model, data) as viewer:
    # Make sure we start in a consistent view
    try:
      viewer.cam.azimuth = 180.0
      viewer.cam.elevation = -10.0
      viewer.cam.distance = 1.2
      viewer.cam.lookat[:] = np.array([0.0, 0.0, 0.2])
    except Exception:
      pass

    start = time.time()
    for _ in range(steps):
      if not viewer.is_running():
        break

      mujoco.mj_step(model, data)
      viewer.sync()

      # Real-time pacing
      target = start + data.time
      now = time.time()
      if target > now:
        time.sleep(target - now)


if __name__ == "__main__":
  main()