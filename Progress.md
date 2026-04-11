# How Far is Video Generation from World Model: A Physical Law Perspective
## Overview
Our scaling experiments show perfect generalization within the distribution, measurable scaling behavior for combinatorial generalization, but failure in out-of-distribution scenarios. Further experiments reveal two key insights about the generalization mechanisms of these models:
1. the models **fail to abstract general physical rules** and instead exhibit **“case-based” generalization behavior** (i.e., mimicking the closest training example)
2. when generalizing to new cases, models are observed to prioritize different factors when referencing training data: **color > size > velocity > shape**. 

Our study suggests that **scaling alone is insufficient for video generation models to uncover fundamental physical laws**.

Video generation is believed to be a promising way toward scalable world models. **However, its capability to learn physical laws from visual observations has not yet been verified.**

## Methonolgy
In this paper, we propose a categorization for a comprehensive evaluation based on the relationship between training and test data. **In-distribution (ID) generalization** assumes that training and testing data are independent and identically distributed. **Out-of distribution (OOD) generalization** refers to the model’s performance on testing data that come from a different distribution than the training data, particularly when latent parameters fall outside the range seen during training.

# PhysTwin: Physics-Informed Reconstruction and Simulation of Deformable Objects from Videos

## Overview:
Our approach centers on two key components: 
1. a **physics-informed representation** that combines **spring-mass models for realistic physical simulation**, generative **shape models for geometry**, and **Gaussian splats for rendering** (物理模拟 + 形状模拟 + 渲染)
2. a novel multi-stage, optimization-based **inverse modeling framework** that reconstructs complete geometry, infers dense physical properties, and replicates realistic appearance from videos. (形状重建 + 密度推断 + 外貌复原)

## Method:
We then present our two-stage:
1. the physics-related optimization
2. appearance-based optimization

**Goal**: minimize the error bewteen prediction $\hat{O}_{t, i}$ and the actual state $O_{t, i}$.
This *cost function* is decomposed into three components: $C = C_{\text{geometry}} + C_{\text{motion}} + C_{\text{render}}$

## Chanllenge and Solution:
1. partial observations from sparse viewpoints (Generative Shape Prior, 利用 生成式形状先验（Trellis），结合超分辨率和注册模块（PnP、非刚性配准、射线投射对齐），得到初始完整几何。)
2. joint optimization of both the discrete topology and physical parameters (Sparse-to-Dense Optimization. 第一阶段：零阶采样优化，假设均匀弹性，得到初始解。第二阶段：基于自研的 可微分 spring-mass 模拟器，用梯度下降细化稠密弹性和碰撞参数。)
3. discontinuities in the dynamic model, along with the long time horizon and dense parameter space, which make continuous optimization difficult.(采用 Gaussian splats + 线性混合蒙皮 (LBS)，让高斯核随邻近质量点运动而动态更新。)

## 改进方向：
将 PhysTwin 扩展到多物体交互与复杂环境。

# Vid2Sim: Generalizable, Video-based Reconstruction of Appearance, Geometry and Physics for Mesh-free Simulation

## Overview:
Vid2Sim first **reconstructs the observed configuration** of the physical system from video using a feed-forward neural network trained to capture physical world knowledge.  A lightweight optimization pipeline **then refines the estimated appearance, geometry, and physical properties** to closely align with video observations within just a few minutes.

## Method:
We **focus on elastic material** modeled by the Neo-Hookean constitutive model to reduce the state space that our feed-forward predictor needs to learn, where **we only predict Young’s modulus $E$, Poisson’s ratio $ν$ and estimated scalar LBS weight**.
0. Mesh-Free,Reduced-Order Simulation: 使用点集去表示物体，物体被表示为一组离散点（而不是网格或体素）。每个点在静止状态下有一个初始位置，模拟时通过控制点（handles）来驱动这些点的运动。通过一个势能方程去更新这些点的位置，when evolving $z_{t}$ at each time step, we usually **sample a small set of key control points**, which is also called cubature points, to save the computational time and memory.
1. Feed-forward Physical System Identification: 用 VideoMAE 提取视频物理特征 → MLP 回归物理参数($E$ and $v$),HyperNetwork 预测 LBS 权重 → LGM 恢复几何与外观 → 得到可模拟的初始结果。
2. Scene-specific Refinement: In our method, we **accelerate the refinement by introducing a Neural Jacobian module**.Then, we optimize the physical parameters, with fine-tuning the LBS and the corresponding Neural Jacibian at the same time, to **match the input videos**. 

## 改进方向：
扩展 Vid2Sim 到多物理场景与跨模态输入。当前工作主要针对 弹性材料，未来可扩展到 流体、颗粒物、塑性材料 等更复杂的物理现象。可以结合 触觉/力传感器数据 或 单视角视频，实现跨模态的物理属性估计。

# ROBOTARENA $\infty$ : SCALABLE ROBOT BENCHMARKING VIA REAL-TO-SIM TRANSLATION
## Overview:
**Real-world evaluation is inherently unscalable.** Human operators must supervise trials and manually reset scenes, which restricts the scale and frequency of evaluations.

We introduce RobotArena $\infty$, **a new benchmarking framework that scales robot evaluation** by deploying policies in automatically constructed simulated environments and assessing them through automatic VLM score and online human preference feedback:
1. We present a **scalable and extensible benchmarking protocol for robotics**, by coupling physics engines, real-to-sim translation and human preference feedback.
2. We introduce a **fully automated reality-to-simulation translation pipeline built upon VLMs**, 2D-to-3D generative models and differentiable rendering.
3. We evaluate **VLAs from labs worldwide across hundreds of environments with thousands of human preferences**, the most extensive robot evaluation to date.
4. We present **key evaluation results** that reveal how current robot policies generalize—or fail to—under distribution shifts.

## 流程
- MAPPING DEMONSTRATION VIDEOS TO SIMULATION：
Our method extracts **five key elements from the demonstration video**:
1. the camera’s **6-DoF pose** relative to the robot body frame (摄影机机位)
2. **3D mesh reconstructions** of task-relevant objects, their orientations, sizes, and material properties:
3. a scene depth map (景深)
4. a clean background image (背景)
5. proportional–derivative control gains.

- EVALUATING ROBOT TASK PROGRESS SCORES WITH VLMS:
Our goal is to **automate success detection and task progress evaluations**. We thus choose to assess task progress **using prompting techniques for vision-language models (VLMs).**

Specifically, a VLM is prompted with a **shuffled sequence** （为了防止model通过时间顺序来判断progress） of video frames, augmented with the initial frame as a zero-progress reference, and **asked to assign progress scores**

## 技术细节（如何实现3D mesh reconstruction, Automated Robot-Camera Calibration）：
To recover each object’s correct 3D pose, we **render 2D image views of the reconstructed 3D mesh and compare them against the 2D object crop**. The view with the most feature matches is selected, and these correspondences are lifted to 3D **using monocular depth estimate** for the real image and simulated depth for the rendered view

**Physical and material properties for the objects are inferred by prompting Gemini** and are then incorporated into the simulation to ensure realistic interactions.

Specifically, we construct a joint angle–conditioned 3D Gaussian model of the robot via differentiable rendering in simulation based on its URDF file. Given a robot demonstration video annotated with per-frame joint angles, we **render the Gaussian robot model and optimize the camera’s 3D translation and orientation to minimize a composite alignment loss with three terms**: 
1. an **RGB loss** penalizing pixel-level appearance differences
2. a **flow loss** enforcing **consistency** between rendered motion fields and optical flow from the video 
3. a **feature loss** aligning DINOv2 embeddings between rendered and observed frames

## 改进方向：
1. 在进行摄像机机位和**3-D重建**时，我们可以采用不同的loss. 例如在Phys Twin中提到的: $L_{total} = l_{\text{geometry}} + l_{\text{motion}} + l_{\text{render}}$. 或者提出一种新的loss: $L_{total} = L_{\text{geometry}} + L_{\text{flow}} + L_{\text{color}}$ for Automated Robot-Camera Calibration and $L_{total} = L_{\text{geometry}} + L_{\text{motion}}$ for 3D mesh reconstruction. 然后使用Phys Twin中提到的分阶段拟合的方式来training.
2. 物体重建的精度与一致性: 当前使用 Hunyuan-3D 等图像到网格生成模型，但这些模型通常在规范坐标系下生成，需额外姿态估计。
3. 物理属性估计的可靠性: 当前通过 Gemini 推理质量、材质等物理属性，但缺乏真实物理测量支持。


# 2026.3.6
## 尝试复现MoReGen:
1. I tried to run the code produced by MoReGen. But failed. Qwen uses a lot of token on debugging, which takes me a lot of time. And the GPU comsumption is very high too. I need to fix it.

# 2026.3.16
## 复现MoReGen:
- 复现确实成功了，但是仅限于论文中的简单物理小实验。对于一个复杂场景，复现的效果确实不好
- 我找到了之前为什么video feedback之后效果越来越差的原因：我忘记改init code的model了。本来应该是gpt来init下一个generation的code的，但是default model似乎是Qwen 2.5, 所以改了之后效果不行。但是有一个需要注意的地方，就是qwen自己改代码效果也是越来越差的，这个原因不清楚
- eval (PISA)发现它loss只会看mask，完全不管背景是什么样的。(mask will extract the motion feature from our video) 可以**尝试把seen 04的mask和seen 01的mask去evaluate，结果发现它们的loss相当的低**. 01的背景是一个欧式的教堂；04的背景感觉像一个工厂的车间，而且里面物体的数量还不一样. (L2: 0.0818761487588909; Chamfer Distance: 0.19338074362212143; IoU: 0.001124466390365763)

# 2026.3.18
## 测试eval
- 为什么这个loss测出来是这样的？是不是我找错mask了？(以下是seen 01和我GitHub中那个不明的鞋子的loss)
Task: sim_default_task

L2: 0.19989225538250033

Chamfer Distance: 0.5364788277490935

IoU: 0.0

## update on 3.20
- 难以置信，这两东西跑出来的loss真是这个。我觉得有必要跑一遍这个PISA的eval的base line. 具体可以看到我生成的两个mask, 它的实现是用mask蒙住图中出现变化的地方, （颜色的变化也算）。
- 第二点，完全复现PISA的eval有点问题，他在提供的sim data/cilp_json.jsonl中没有给我们提供必要的"points", "num_obj", "points["negative"]", "points["positive]", 导致直接复现它的代码不行。所以我用了第二招：使用sam2论文中给我的Automatic Mask Generator来生成mask, 发现它生成的mask和论文中提供的mask不太一样. 以下是这几个mask间的L2 loss，CD, IoU:

| L2 Loss | mydemo | 论文mask | mymask |
| :---    | :---   | :---       | :---   |
| mydemo  | 0      | 0.19989 | 0.22731   |
| 论文mask | ---   | 0       | 0.20285  |
| my mask | ---    | ---     | 0         |

| CD | mydemo | 论文mask | mymask |
| :---    | :---   | :---       | :---   |
| mydemo  | 0      | 0.53647 | 0.67378   |
| 论文mask | ---   | 0       | 0.53703  |
| my mask | ---    | ---     | 0         |

| IoU | mydemo | 论文mask | mymask |
| :---    | :---   | :---       | :--- |
| mydemo  | 0      | 0.0 | 0.74193   |
| 论文mask | ---   | 0       | 0.0  |
| my mask | ---    | ---     | 0    |

注：原论文中它的结果差不多是：L2: 0.036， CD: 0.08，IoU: 0.165

我知道为什么这个两个不太一样了，好像不指定物体数量的话，这个mask的背景会一直闪烁

Idea:
1. 我发现它这个loss只看mask, 而mask只是把运动、变化的物体给提取出来。所以背景是什么压根无所谓，我们可以先忽略背景，直接生成物体
2. 我发现它mask生成物体运动的效果还不错。挺像剪影的。所以有没有一种可能：我喂给这个agent的不是原视频，而是这个mask? 因为我试了让agent (GPT 5.2, Gemini 3.5)根据视频写文字prompt, 效果并不是很好。可以看的出来它们专注于描述复杂的背景，不擅长描述物体怎么动的。即便我强行要求GPT忽视背景，描述物体的运动，它描述的也不是很好 (描述没有主次，明明是往下掉，它却花了大篇幅描述物体掉到地上怎么左右滚的...), 所以可不可以给agent看mask, 让他写出来生成mask的模拟

## update on 3.21
我通过加points的方法发现可以通过添加点的方式来达到论文中mask的效果，但是这个方法不是很能持续...

下面是对generate_mask.py和clip_json.json的修改：
```python
# 这里如果自己去猜这个points会让返回的array.shape不是(V, N, H, W)而是(V, H, W)
# 为了解决这个问题，我要加一点代码：
ADD_POINTS = True

# ...
masks = (masks > 0.0).cpu().numpy() # [num_frames, num_objects, height, width]
if ADD_POINTS:
    # 假设 masks 的 shape 是 (V, H, W)，而你知道 num_objects = 1
    masks = np.expand_dims(masks, axis=1)   # 变成 (V, 1, H, W)

np.savez_compressed(mask_path, mask=masks)
```

```json
{
  "prompt": "A shoe falls. You need to generate video that conforms to the laws of physics.", 
  "points": [
      {
        "positive": [[613, 439]], 
        "negative": [[466, 439], [328, 439]]
      }
    ]
}
```


# 2026.3.28
## 调研现有benchmark
In the MoReGen paper, I find that they cite several benchmark to illustrate the advancement of their benchmark, MoReGen (that benchmark haven't public yet). However, it seems like that they didn't test all of these benchmark. Such as PISA benchmark, I don't think it is runnable. The benchmark lack of serval key labels: positive points and negative points, which tell the mask generator to **trace which object (positive points)**, and **do not trace which one (nagative points)**. I tried to raise the issue, but no one reply. Also, I have sent the email to the author, but he didn't reply me too.

Then, I notice that in the paper, they use **benchmark Trajan and VideoPhys** for evaluation. So, I decided to look at it.

## VideoPhys
It mainly evaluates two thing:
- Semantic Adherence (SA): 观察你生成的视频是不是和你的prompt一致。SA = 1, 一致；SA = 0， 不一致
- Physical Commonsense (PC): 观察物体的运动是不是遵循physical law. PC = 1，遵循物理定律；PC = 0，不遵循物理定律

注：在VideoPhys2中，它有增加了一条评价标准Physical Rules, 并且增加了SA和PC的评价打分方式(into 5-point scale)：
- Semantic Adherence (SA): 1: Very Unlikely; 2: Unlikely; 3: Neutral; 4: Likely; 5: Very Likely
- Physical Commonsense (PC): 1: Very Unlikely; 2: Unlikely; 3: Neutral; 4: Likely; 5: Very Likely
- Physical Rules (PR): 观察视频是否遵循了physical law.  0: violated; 1: followed; 2: cannot be determined

他又加了一种joint performance的评价方法：$SA \ge 4$ and $PC \ge 4$

注：他这个peft和transformer不太兼容；要把peft的版本调到0.10.1

可以在demo中看到他给定的target output (output_sa.csv)和我复现出来的output (my_output_sa.csv), 它们不太一样...
SA部分my_output和output相差了5组；PC部分有两个不一样的；PR部分有一个不一样的。这个原因不明

VideoCon‑Physics是他训练的模型(7B), 用regression去predict SA, PC; 用classification去predict PR.

## Trajan
It mainly focus on **The Trajectory of the object**.

注：不同于普通的轨迹对比(Trajectory L2 loss), 这个model可以在没有对比视频的情况下进行evaluate. 这是因为这个model可以通过轨迹重建的方式观察你这个视频的重建误差，误差大就说明运动轨迹不合理.

# 2026.4.9
## Kubric
上周去装了一下kubric, 发现kubric建议使用docker去装；没办法，只能往ssh里面装docker了。国内的服务器没法安装docker, 因为被墙拦住了。我打算这周去试试国外的服务器，比如AWS和Google

## pybullet
同时，我在测试pybullet.
1. 安装方面：
      - pybullet和manim不一样，它没有现成的CLI文档；所以直接调用bin\python即可
      - pybullet似乎不支持mp4视频的输出。不过无所谓，mp4视频本来就不是必须要的，我问了一下GPT，它给我的建议是直接输出逐帧的RBG的jpg图片，然后将query_vedio(use_frames = True, ...)即可; 它给我的query_video函数有原生的支持
2. 调试方面：
      - 第一，pybullet实际上是鼓励你使用mesh/URDF的。虽然直接使用create collision shape可以在我们的代码里创建geom; 但是这样出来的效果并不理想。(from Deepseek: 在pybullet中，loadURDF是绝对主流的想法，而选择更底层的API，如createCollisionShape则用于处理特定或临时的几何体)
      - 第二，pybullet在使用URDF时，如果要指定inertia, inertia的计算不能出错，否则有可能出现物体下落的很缓慢的情况。以下时inertia的计算公式(for a box)：
        $$
        \begin{aligned}
        I_{xx} &= \frac{m}{12}(y^{2} + z^{2}) \\
        I_{yy} &= \frac{m}{12}(x^{2} + z^{2}) \\
        I_{zz} &= \frac{m}{12}(x^{2} + y^{2}) \\
        I_{xy} = I_{yz} = I_{xz} &= 0
        \end{aligned}
        $$
      - 第三，