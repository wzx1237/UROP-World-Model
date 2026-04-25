import pybullet as p
import pybullet_data
import time

def init_sim(gui=True, gravity=-0.01, time_step=1/240.0):
    if gui:
        p.connect(p.GUI)
    else:
        p.connect(p.DIRECT)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, gravity)
    p.setTimeStep(time_step)

    # 加载地面
    plane_id = p.loadURDF("plane.urdf")
    return plane_id

def create_box(half_extents, mass, base_position, base_orientation=(0, 0, 0, 1)):
    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX, halfExtents=half_extents
    )
    body_id = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=-1,
        basePosition=base_position,
        baseOrientation=base_orientation
    )
    return body_id

def create_sphere(radius, mass, base_position, base_orientation=(0, 0, 0, 1)):
    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_SPHERE, radius=radius
    )
    body_id = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=-1,
        basePosition=base_position,
        baseOrientation=base_orientation
    )
    return body_id

def create_cylinder(radius, height, mass, base_position, base_orientation=(0, 0, 0, 1)):
    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_CYLINDER, radius=radius, height=height
    )
    body_id = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=-1,
        basePosition=base_position,
        baseOrientation=base_orientation
    )
    return body_id

def create_mesh(mesh_path, scale, mass, base_position, base_orientation=(0, 0, 0, 1)):
    collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_MESH, fileName=mesh_path, meshScale=scale
    )
    # Added visual shape with Yellow color [1, 1, 0, 1]
    visual_shape = p.createVisualShape(
        shapeType=p.GEOM_MESH, fileName=mesh_path, meshScale=scale, rgbaColor=[1, 1, 0, 1]
    )
    body_id = p.createMultiBody(
        baseMass=mass,
        baseCollisionShapeIndex=collision_shape,
        baseVisualShapeIndex=visual_shape,
        basePosition=base_position,
        baseOrientation=base_orientation
    )
    return body_id

def run_simulation(steps=2400, sleep=True):
    for _ in range(steps):
        p.stepSimulation()
        if sleep:
            time.sleep(1/240.0)

if __name__ == "__main__":
    init_sim(gui=True)

    # 1. Create the Yellow Shoe
    # Using 'teddy_vhacd.obj' as a mesh proxy because it is organic/rounded 
    # and rolls much better than a primitive box.
    shoe_path = r"C:\Users\15712\Desktop\UROP\pybullet\shoe\shoe.urdf" 
    
    # Scale it to look like a shoe (long in Y, short in X/Z)
    shoe_scale = [1, 1, 1]
    start_pos = [0, 0, 1.5]
    # Tilt it so it hits the ground on its "heel"
    start_orientation = p.getQuaternionFromEuler([-1.2, 0, 0])

    shoe_id = p.loadURDF(
        "basic0.urdf",
        basePosition=start_pos,
        baseOrientation=start_orientation,
        globalScaling=1.2
    )
    # shoe_id = create_mesh(
    #     mesh_path=shoe_path,
    #     scale=shoe_scale,
    #     mass=0.4,
    #     base_position=start_pos,
    #     base_orientation=start_orientation
    # )

    # 2. Physics Tuning for "Roll back a circle"
    # Low rolling friction allows the object to continue rotating after hitting the ground.
    # High restitution (bounciness) helps it kick back.
    p.changeDynamics(
        shoe_id, -1, 
        restitution=0.6, 
        lateralFriction=0.5, 
        rollingFriction=0.001, 
        spinningFriction=0.001
    )


    # 4. Run simulation
    # 2400 steps is roughly 10 seconds, plenty of time to watch the roll and stop.
    run_simulation(steps=1500)

    p.disconnect()