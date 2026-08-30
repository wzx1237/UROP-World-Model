This file will provide some pybullet code template and FAQ for API reference:

## Template:

For creating simple shape:
```python
import pybullet as p
def init_sim(gui=True, gravity=-9.81, time_step=1/240.0):
    if gui:
        p.connect(p.GUI)
    else:
        p.connect(p.DIRECT)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, gravity)
    p.setTimeStep(time_step)

    # load the ground
    plane_id = p.loadURDF("plane.urdf")
    return plane_id

def create_box(half_extents, mass, color, base_position, base_orientation=(0, 0, 0, 1)):
    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX, halfExtents=half_extents
    )
    vis_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX, halfExtents=half_extents, rgbaColor=color
    )
    body_id = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=vis_shape,
        basePosition=base_position,
        baseOrientation=base_orientation
    )
    return body_id
```

For import URDF file:
```python
import pybullet as p
def load_URDF(urdf_path, basePosition, baseOrientation, globalScaling=1.0):
    mesh = p.loadURDF(urdf_path, basePosition, baseOrientation, globalScaling)
    return mesh
```

Use it like this:
```python
obj = load_URDF('/homes/zwanglg/wzxhome/meshes/basic.urdf', [0, 0, 1.5], p.getQuaternionFromEuler([0, 0, 0]), 1.2)
p.changeDynamics(
        obj, -1, 
        restitution=0.6, 
        lateralFriction=0.5, 
        rollingFriction=0.001, 
        spinningFriction=0.001
)
```

## FAQ:
If you facing the following feedback, you may find the corresponding suggestion below:
1. if you need to import some urdf file, try to find it in: /homes/zwanglg/wzxhome/meshes
    This may help you.
2. feedback: ... that defies typical physical laws of gravity
    that might means: the object in the result video falls very slow or the object is fixed in the air. To solve this, you need to check:
        - whether you set the gravity correctly (correct value: -9.81)
        - check you fps or timeStep; if your default timeStep is much smaller than 1/fps, the object might fall slowly. Here is a suggested improvement from GPT:
            ```python
            fps = 30
            physics_hz = 240
            substeps = physics_hz // fps        # 240/30 = 8

            p.setRealTimeSimulation(0)
            p.setTimeStep(1.0 / physics_hz)

            for frame_idx in range(total_frames):
                for _ in range(substeps):
                    p.stepSimulation()
                # then, save this frame
            ```