# Star Robot Reach 环境奖励函数详解

## 📊 奖励函数总览

Reach 环境的总奖励由 **5 个奖励项**组成：

| 奖励项 | 权重 | 类型 | 作用 |
|--------|------|------|------|
| `end_effector_position_tracking` | **-0.2** | 惩罚 | 末端位置误差 |
| `end_effector_position_tracking_fine_grained` | **+0.1** | 奖励 | 精细位置跟踪 |
| `end_effector_orientation_tracking` | **-0.1** | 惩罚 | 末端方向误差 |
| `action_rate` | **-0.0001** | 惩罚 | 动作变化率 |
| `joint_vel` | **-0.0001** | 惩罚 | 关节速度 |

### 总奖励计算

```python
total_reward = (
    -0.2 * position_error +           # 位置误差惩罚
    +0.1 * position_fine_reward +     # 精细位置奖励
    -0.1 * orientation_error +        # 方向误差惩罚
    -0.0001 * action_rate_penalty +   # 动作平滑惩罚
    -0.0001 * joint_vel_penalty       # 速度惩罚
)
```

## 🎯 详细奖励项解释

### 1. **末端位置跟踪** (Position Tracking)

#### A. 粗粒度位置误差 (`end_effector_position_tracking`)

**配置**:
```python
end_effector_position_tracking = RewTerm(
    func=mdp.position_command_error,
    weight=-0.2,  # 负权重 = 惩罚
    params={
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "command_name": "ee_pose"
    },
)
```

**实现** (在 `mdp/rewards.py`):
```python
def position_command_error(env, command_name, asset_cfg):
    """计算末端执行器与目标位置的 L2 距离"""
    # 获取目标位置
    des_pos = command[:, :3]  # (x, y, z)
    
    # 获取当前末端位置
    curr_pos = asset.data.body_pos_w[:, body_id]
    
    # 计算欧式距离
    distance = ||curr_pos - des_pos||
    
    return distance  # 单位：米
```

**奖励值**:
```python
reward = -0.2 * distance

# 例子：
# distance = 0.1 m  → reward = -0.02
# distance = 0.01 m → reward = -0.002
# distance = 0.001 m → reward = -0.0002
```

**特点**:
- ✅ 简单直接的距离惩罚
- ✅ 鼓励机器人尽快接近目标
- ⚠️ 在远距离时惩罚很大

#### B. 精细位置跟踪 (`end_effector_position_tracking_fine_grained`)

**配置**:
```python
end_effector_position_tracking_fine_grained = RewTerm(
    func=mdp.position_command_error_tanh,
    weight=0.1,  # 正权重 = 奖励
    params={
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "std": 0.1,  # 标准差参数
        "command_name": "ee_pose"
    },
)
```

**实现**:
```python
def position_command_error_tanh(env, std, command_name, asset_cfg):
    """使用 tanh 函数平滑奖励"""
    distance = ||curr_pos - des_pos||
    
    # tanh 映射：将距离映射到 [0, 1]
    reward = 1 - tanh(distance / std)
    
    return reward
```

**奖励曲线**:
```python
std = 0.1 m

distance (m)  →  reward
0.000         →  1.000  (完美)
0.010         →  0.900  (很好)
0.050         →  0.622  (中等)
0.100         →  0.238  (较差)
0.200         →  0.035  (很差)
```

**特点**:
- ✅ 在接近目标时给予高奖励
- ✅ 距离越近，奖励越高（非线性）
- ✅ 适合精细控制

**可视化**:
```
奖励值
1.0 |     *
    |    *
0.8 |   *
    |  *
0.6 | *
    |*
0.4 |*
    |
0.2 |*
    |
0.0 |_______________
    0  0.1  0.2  距离(m)
```

### 2. **末端方向跟踪** (`end_effector_orientation_tracking`)

**配置**:
```python
end_effector_orientation_tracking = RewTerm(
    func=mdp.orientation_command_error,
    weight=-0.1,  # 负权重 = 惩罚
    params={
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "command_name": "ee_pose"
    },
)
```

**实现**:
```python
def orientation_command_error(env, command_name, asset_cfg):
    """计算四元数角度误差"""
    # 获取目标方向（四元数）
    des_quat = command[:, 3:7]  # (qw, qx, qy, qz)
    
    # 获取当前方向
    curr_quat = asset.data.body_quat_w[:, body_id]
    
    # 计算四元数误差（弧度）
    angle_error = quat_error_magnitude(curr_quat, des_quat)
    
    return angle_error  # 单位：弧度
```

**奖励值**:
```python
reward = -0.1 * angle_error

# 例子：
# angle_error = 0.1 rad (5.7°)  → reward = -0.01
# angle_error = 0.01 rad (0.57°) → reward = -0.001
# angle_error = 0.0 rad (0°)     → reward = 0.0
```

### 3. **动作平滑惩罚** (`action_rate`)

**配置**:
```python
action_rate = RewTerm(
    func=mdp.action_rate_l2,
    weight=-0.0001,  # 很小的惩罚
)
```

**实现**:
```python
def action_rate_l2(env):
    """惩罚动作变化过大"""
    # 计算当前动作与上一步动作的差异
    action_diff = current_action - last_action
    
    # L2 范数
    rate = ||action_diff||²
    
    return rate
```

**目的**:
- ✅ 鼓励平滑控制
- ✅ 避免突然的动作变化
- ✅ 减少机械磨损

### 4. **关节速度惩罚** (`joint_vel`)

**配置**:
```python
joint_vel = RewTerm(
    func=mdp.joint_vel_l2,
    weight=-0.0001,  # 很小的惩罚
    params={"asset_cfg": SceneEntityCfg("robot")},
)
```

**实现**:
```python
def joint_vel_l2(env, asset_cfg):
    """惩罚高关节速度"""
    joint_velocities = robot.data.joint_vel
    
    # L2 范数
    vel_penalty = ||joint_velocities||²
    
    return vel_penalty
```

**目的**:
- ✅ 鼓励缓慢、稳定的运动
- ✅ 避免剧烈运动
- ✅ 提高安全性

## 📈 课程学习 (Curriculum Learning)

奖励权重会随训练进度动态调整：

```python
class CurriculumCfg:
    # action_rate 权重变化
    action_rate = CurrTerm(
        func=mdp.modify_reward_weight,
        params={
            "term_name": "action_rate",
            "weight": -0.005,      # 目标权重（50倍增加）
            "num_steps": 4500      # 在 4500 步内线性增加
        }
    )
    
    # joint_vel 权重变化
    joint_vel = CurrTerm(
        func=mdp.modify_reward_weight,
        params={
            "term_name": "joint_vel",
            "weight": -0.001,      # 目标权重（10倍增加）
            "num_steps": 4500
        }
    )
```

**效果**:
```
训练步数         action_rate 权重    joint_vel 权重
0               -0.0001             -0.0001
1000            -0.0011             -0.0003
2000            -0.0021             -0.0005
3000            -0.0031             -0.0007
4500+           -0.005              -0.001
```

**目的**:
- 早期：允许大幅度动作，快速学习
- 后期：强制平滑控制，精细调整

## 🎯 目标位置生成

**配置**:
```python
ee_pose = mdp.UniformPoseCommandCfg(
    asset_name="robot",
    body_name="endo360_needle",
    resampling_time_range=(4.0, 4.0),  # 每 4 秒重新采样
    debug_vis=True,  # 显示目标点
    ranges=mdp.UniformPoseCommandCfg.Ranges(
        pos_x=(0.35, 0.65),   # X: 35-65 cm
        pos_y=(-0.2, 0.2),    # Y: ±20 cm
        pos_z=(0.15, 0.5),    # Z: 15-50 cm
        roll=(0.0, 0.0),      # Roll: 固定 0°
        pitch=(math.pi, math.pi),  # Pitch: 固定 180° (向下)
        yaw=(-3.14, 3.14),    # Yaw: 全范围 ±180°
    ),
)
```

**工作空间**:
```
        Y
        ↑
        |  20cm
        |_____ X
       /  
      / Z
     ↙

X: 35-65 cm (前方)
Y: ±20 cm (左右)
Z: 15-50 cm (高度)
```

## 💯 奖励值范围估计

### 最佳情况（完美跟踪）
```python
position_error = 0.001 m
orientation_error = 0.01 rad
action_rate = 0.01
joint_vel = 0.01

reward = -0.2 * 0.001 +        # -0.0002
         +0.1 * 0.99 +          # +0.099
         -0.1 * 0.01 +          # -0.001
         -0.0001 * 0.01 +       # -0.000001
         -0.0001 * 0.01         # -0.000001
       ≈ +0.098                 # 正奖励
```

### 最差情况（远离目标）
```python
position_error = 0.5 m
orientation_error = 1.0 rad
action_rate = 1.0
joint_vel = 10.0

reward = -0.2 * 0.5 +          # -0.1
         +0.1 * 0.0 +           # 0.0
         -0.1 * 1.0 +           # -0.1
         -0.0001 * 1.0 +        # -0.0001
         -0.0001 * 10.0         # -0.001
       ≈ -0.201                 # 负奖励
```

### 典型情况（学习中）
```python
position_error = 0.05 m
orientation_error = 0.1 rad
action_rate = 0.1
joint_vel = 1.0

reward ≈ +0.03                  # 小正奖励
```

## 🔧 如何调整奖励

如果你想修改奖励函数，编辑你的环境配置文件：

`source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`

### 示例：增加位置精度要求

```python
class StarReachEnvCfg(ReachEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        
        # 增加位置误差惩罚
        self.rewards.end_effector_position_tracking.weight = -0.5  # 从 -0.2 增加
        
        # 减小 tanh 标准差，要求更高精度
        self.rewards.end_effector_position_tracking_fine_grained.params["std"] = 0.05  # 从 0.1 减小
```

### 示例：增加动作平滑要求

```python
# 在 __post_init__ 中
self.rewards.action_rate.weight = -0.001  # 从 -0.0001 增加 10 倍
self.rewards.joint_vel.weight = -0.001    # 从 -0.0001 增加 10 倍
```

### 示例：只关注位置，忽略方向

```python
# 禁用方向跟踪
self.rewards.end_effector_orientation_tracking.weight = 0.0  # 从 -0.1 设为 0
```

## 📊 训练监控

在训练过程中，你可以在 TensorBoard 中看到每个奖励项的值：

```bash
tensorboard --logdir logs/rsl_rl/star_reach/
```

**关键指标**:
- `Episode Reward`: 总奖励（应该随训练增加）
- `position_tracking`: 位置误差（应该随训练减小）
- `orientation_tracking`: 方向误差（应该随训练减小）
- `action_rate`: 动作平滑度
- `joint_vel`: 关节速度

## 🎓 奖励设计原则

当前奖励函数的设计遵循：

1. **主要目标** (权重大):
   - 位置跟踪: -0.2 和 +0.1
   - 方向跟踪: -0.1

2. **次要目标** (权重小):
   - 动作平滑: -0.0001
   - 速度控制: -0.0001

3. **平衡**:
   - 正负奖励结合（粗粒度惩罚 + 精细奖励）
   - 任务目标 vs 行为约束

4. **课程学习**:
   - 早期：任务优先
   - 后期：行为优化

## ✅ 总结

Star Robot Reach 环境的奖励函数设计：

✅ **优点**:
- 明确的任务目标（位置 + 方向）
- 精细和粗粒度奖励结合
- 鼓励平滑控制
- 支持课程学习

⚙️ **可调参数**:
- 奖励权重
- tanh 标准差
- 工作空间范围
- 课程学习进度

🎯 **训练目标**:
- 精确控制针尖到达目标位置
- 保持正确的方向
- 平滑、稳定的运动

---

**文档位置**: 
- 奖励配置: `reach_env_cfg.py` (第 133-161 行)
- 奖励实现: `mdp/rewards.py`

