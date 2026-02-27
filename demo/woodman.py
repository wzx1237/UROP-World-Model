import pybullet as p
import pybullet_data

# 连接到物理引擎
p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# 设置重力
p.setGravity(0, 0, -9.8)

# 加载地面
plane_id = p.loadURDF("plane.urdf")

# 创建一个绿色球体
radius = 0.2
mass = 1

# 碰撞形状
collision_shape = p.createCollisionShape(
    shapeType=p.GEOM_SPHERE,
    radius=radius
)

# 可视化形状（绿色）
visual_shape = p.createVisualShape(
    shapeType=p.GEOM_SPHERE,
    radius=radius,
    rgbaColor=[0, 1, 0, 1]   # RGBA: 绿色
)

# 创建球体刚体
sphere_id = p.createMultiBody(
    baseMass=mass,
    baseCollisionShapeIndex=collision_shape,
    baseVisualShapeIndex=visual_shape,
    basePosition=[0, 0, 1]   # 初始位置在空中
)

# 模拟一段时间
for _ in range(1000):
    p.stepSimulation()

# 保持窗口
input("Press Enter to exit...")
p.disconnect()
