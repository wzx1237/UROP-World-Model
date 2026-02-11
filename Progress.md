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
1. partial observations from sparse viewpoints (Generative Shape Prior)
2. joint optimization of both the discrete topology and physical parameters (Sparse-to-Dense Optimization.)
3. discontinuities in the dynamic model, along with the long time horizon and dense parameter space, which make continuous optimization difficult.

## 改进方向：
