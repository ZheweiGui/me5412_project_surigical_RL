# Star Robot 环境配置指南

本指南将帮助你配置使用 `star.usd` 机器人的强化学习环境，类似于 `Isaac-Reach-Franka-v0`。

## 📁 已创建的文件

以下文件已经为你创建：

### 1. 机器人资产配置
```
source/isaaclab_assets/isaaclab_assets/robots/star.py
```
定义 Star 机器人的物理属性、关节配置和执行器参数。

### 2. 环境配置
```
source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/star/
├── __init__.py                    # 环境注册
├── joint_pos_env_cfg.py          # 环境配置
└── agents/
    ├── __init__.py
    └── rsl_rl_ppo_cfg.py         # PPO 训练配置
```

### 3. 测试脚本
```
test_star_env.py                   # 测试环境是否正确配置
```

## 🔧 必需的配置步骤

### 步骤 1: 检查 star.usd 文件中的关节信息

首先，你需要了解 `star.usd` 中的关节结构。在 Isaac Sim 中打开文件：

```bash
# 启动 Isaac Sim
./isaaclab.sh -s

# 在 Isaac Sim 中打开: 
# File -> Open -> 选择 source/isaaclab_assets/isaaclab_assets/robots/star.usd
```

在 **Stage** 窗口中，找到并记录：
- 所有关节的名称（例如：`joint1`, `joint2`, ...）
- 末端执行器（end-effector）的名称（例如：`end_effector`, `ee_link`, `tool0`）
- 如果有抓手，记录抓手关节名称

### 步骤 2: 配置机器人资产文件

编辑 `source/isaaclab_assets/isaaclab_assets/robots/star.py`：

```python
init_state=ArticulationCfg.InitialStateCfg(
    joint_pos={
        # 替换为你的实际关节名称和初始位置
        "joint1": 0.0,
        "joint2": -0.5,
        "joint3": 0.0,
        "joint4": -2.0,
        "joint5": 0.0,
        "joint6": 2.0,
        "joint7": 0.7,
        # 如果有抓手
        "gripper_joint.*": 0.04,
    },
    joint_vel={".*": 0.0},
),
actuators={
    # 配置主要关节执行器
    "star_main_joints": ImplicitActuatorCfg(
        joint_names_expr=["joint[1-7]"],  # 根据实际关节名称修改
        effort_limit_sim=87.0,
        stiffness=80.0,
        damping=4.0,
    ),
    # 如果有抓手，单独配置
    "star_gripper": ImplicitActuatorCfg(
        joint_names_expr=["gripper_joint.*"],
        effort_limit_sim=200.0,
        stiffness=2e3,
        damping=1e2,
    ),
},
```

### 步骤 3: 配置环境文件

编辑 `source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`：

```python
# 设置末端执行器名称
END_EFFECTOR_NAME = "end_effector"  # 替换为实际名称

# 配置动作空间（关节控制）
self.actions.arm_action = mdp.JointPositionActionCfg(
    asset_name="robot", 
    joint_names=["joint.*"],  # 替换为实际关节名称模式
    scale=0.5, 
    use_default_offset=True
)

# 配置末端执行器方向
self.commands.ee_pose.ranges.pitch = (math.pi, math.pi)  # 根据末端执行器轴向调整
```

### 步骤 4: 测试环境

运行测试脚本检查配置：

```bash
python test_star_env.py
```

如果出现错误，请根据错误信息调整配置。

## 🚀 训练你的模型

配置完成后，可以开始训练：

```bash
# 使用 RSL-RL 训练
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Reach-Star-v0 \
    --num_envs 4096 \
    --headless

# 查看训练结果（推理模式）
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --load_run <运行文件夹名称>
```

## 📊 环境详情

### 注册的环境

- **`Isaac-Reach-Star-v0`**: 训练环境
  - 使用关节位置控制
  - 目标：控制末端执行器到达目标位置和方向

- **`Isaac-Reach-Star-Play-v0`**: 推理/演示环境
  - 较少的环境数量（50 vs 4096）
  - 禁用观察噪声
  - 用于可视化训练结果

### 环境参数（与 Franka Reach 一致）

- **观察空间**: 机器人状态（关节位置、速度）+ 目标位置
- **动作空间**: 关节位置增量
- **奖励函数**:
  - 末端执行器位置跟踪
  - 末端执行器方向跟踪
  - 动作平滑度惩罚

## ❓ 常见问题

### 1. 环境无法加载

**错误**: `Failed to create prim at path...`

**解决方案**: 
- 检查 `star.usd` 文件路径是否正确
- 确保文件在 `source/isaaclab_assets/isaaclab_assets/robots/star.usd`

### 2. 关节控制不工作

**错误**: `No joints found matching pattern...`

**解决方案**:
- 在 Isaac Sim 中打开 `star.usd`，确认关节名称
- 更新 `star.py` 和 `joint_pos_env_cfg.py` 中的关节名称模式

### 3. 末端执行器位置不正确

**解决方案**:
- 确认 `END_EFFECTOR_NAME` 设置正确
- 在 USD 文件中查找正确的 body/link 名称

### 4. 机器人行为异常

**解决方案**:
- 调整执行器参数（stiffness, damping）
- 检查初始关节位置是否合理
- 确保关节限制在有效范围内

## 🔍 调试技巧

### 查看机器人信息

```python
import gymnasium as gym
import isaaclab_tasks

env = gym.make("Isaac-Reach-Star-v0", num_envs=1)
env.reset()

# 打印机器人信息
robot = env.unwrapped.scene["robot"]
print("关节名称:", robot.data.joint_names)
print("Body 名称:", robot.data.body_names)
```

### 可视化调试

启动时不使用 `--headless` 标志：

```bash
./isaaclab.sh -p test_star_env.py  # 会打开可视化窗口
```

## 📚 参考资料

- **Franka Reach 环境**: `source/isaaclab_tasks/.../reach/config/franka/`
- **IsaacLab 文档**: `docs/source/overview/environments.rst`
- **训练指南**: `docs/source/overview/reinforcement-learning/training_guide.rst`

## ✅ 检查清单

配置完成后，确保：

- [ ] `star.usd` 文件在正确位置
- [ ] `star.py` 中的关节名称与 USD 文件匹配
- [ ] 末端执行器名称配置正确
- [ ] 执行器参数已根据机器人规格调整
- [ ] 测试脚本运行成功
- [ ] 环境可以正常 reset 和 step

---

如有问题，请检查以下文件的配置是否正确：
1. `source/isaaclab_assets/isaaclab_assets/robots/star.py`
2. `source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`

