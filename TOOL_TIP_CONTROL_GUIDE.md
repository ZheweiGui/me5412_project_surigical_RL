# Star Robot 工具末端控制配置指南

## 🎯 问题描述

默认配置控制的是**机械臂末端** (`star_link_ee`)，但实际需要控制的是**工具末端**（如针尖）。

## ✅ 已修复

### 修改内容

**文件**: `source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`

**修改前**:
```python
END_EFFECTOR_NAME = "star_link_ee"  # 机械臂末端
```

**修改后**:
```python
END_EFFECTOR_NAME = "endo360_needle"  # 工具末端（针尖）
```

### 效果

- ✅ 目标位置点现在在工具的实际末端（针尖）
- ✅ 位置跟踪奖励基于工具末端位置
- ✅ 方向跟踪奖励基于工具末端方向

## 🔄 可用的末端执行器选项

根据你的 USD 文件结构，有以下可选的末端执行器：

### 选项对比

| 名称 | 位置 | 用途 | 推荐度 |
|------|------|------|--------|
| `star_link_ee` | 机械臂末端 | 不考虑工具时使用 | ⭐⭐ |
| `ati` | 力传感器 | 需要力控制时使用 | ⭐⭐⭐ |
| `endo360_link_1` | 工具主体末端 | 控制工具本体 | ⭐⭐⭐ |
| `endo360_needle` | 针尖 | 精确控制针尖位置 | ⭐⭐⭐⭐⭐ |
| `endo360_calibrated` | 校准点 | 特殊校准任务 | ⭐⭐⭐ |

### 如何选择

**场景 1: 精确插入任务（推荐当前设置）**
```python
END_EFFECTOR_NAME = "endo360_needle"  # 针尖
```
适用于：针刺、插入、精确定位等任务

**场景 2: 力控制任务**
```python
END_EFFECTOR_NAME = "ati"  # 力传感器位置
```
适用于：接触检测、力反馈控制

**场景 3: 工具本体控制**
```python
END_EFFECTOR_NAME = "endo360_link_1"  # 工具主体
```
适用于：整体工具定位、避障等

**场景 4: 不考虑工具**
```python
END_EFFECTOR_NAME = "star_link_ee"  # 仅机械臂
```
适用于：测试机械臂本身、无工具场景

## 📐 工具链接层级结构

```
world
  └── star_link_0 (base)
       └── star_link_1
            └── star_link_2
                 └── ...
                      └── star_link_7
                           └── star_link_ee (机械臂末端)
                                └── ati (力传感器)
                                     └── endo360_link_0
                                          └── endo360_link_1
                                               └── endo360_needle (针尖) ⭐
                                               └── endo360_calibrated
```

## 🎮 使用方法 2: TCP 偏移（高级）

如果你想保持 `star_link_ee` 作为参考，但在其基础上添加偏移到工具末端：

```python
# 在 joint_pos_env_cfg.py 中
import isaaclab.utils.math as math_utils

# 计算从 star_link_ee 到 endo360_needle 的偏移
# 这需要知道实际的偏移距离（单位：米）
TOOL_OFFSET = [0.0, 0.0, 0.2]  # 示例：沿 Z 轴偏移 20cm

# 在奖励计算中添加偏移
# 注意：这需要修改奖励函数，较为复杂
```

**推荐**: 直接使用工具末端 body（方法 1）更简单直接。

## 🧪 验证配置

### 测试脚本

运行以下命令验证末端执行器配置：

```bash
python test_star_env.py
```

### 可视化检查

启动带可视化的训练：

```bash
./train_star_reach.sh --visual
```

在可视化界面中，你应该看到：
- 🎯 目标点（红色球体）出现在针尖位置
- 📏 机器人尝试移动针尖到达目标
- ✅ 奖励基于针尖与目标的距离

## 🔍 调试技巧

### 检查末端执行器位置

```python
import gymnasium as gym
import isaaclab_tasks

env = gym.make("Isaac-Reach-Star-v0", num_envs=1)
env.reset()

robot = env.unwrapped.scene["robot"]

# 打印所有 body 名称
print("可用的 body:", robot.data.body_names)

# 获取针尖位置
needle_idx = robot.find_bodies("endo360_needle")[0][0]
needle_pos = robot.data.body_pos_w[:, needle_idx, :]
print(f"针尖位置: {needle_pos}")
```

### 切换不同的末端执行器

只需修改一行配置：

```python
# 在 joint_pos_env_cfg.py 中
END_EFFECTOR_NAME = "endo360_needle"  # 改为其他 body 名称
```

然后重新运行训练。

## ⚠️ 注意事项

### 1. 工具链接必须正确连接

确保 USD 文件中工具正确地附加在机械臂末端，否则工具位置可能不正确。

### 2. 工作空间范围

使用工具末端后，工作空间会扩大（因为工具增加了额外长度）。可能需要调整命令生成器的范围：

```python
# 在 joint_pos_env_cfg.py 中
self.commands.ee_pose.ranges.pos_x = (0.3, 0.7)  # 根据实际情况调整
self.commands.ee_pose.ranges.pos_y = (-0.3, 0.3)
self.commands.ee_pose.ranges.pos_z = (0.1, 0.6)
```

### 3. 方向约束

针尖的方向可能与机械臂末端不同，可能需要调整方向约束：

```python
# 在 joint_pos_env_cfg.py 中
# 如果针沿不同方向，调整这些参数
self.commands.ee_pose.ranges.roll = (-0.5, 0.5)
self.commands.ee_pose.ranges.pitch = (math.pi - 0.5, math.pi + 0.5)
self.commands.ee_pose.ranges.yaw = (-3.14, 3.14)
```

## 📊 对比效果

| 方面 | star_link_ee | endo360_needle |
|------|--------------|----------------|
| 控制精度 | 机械臂末端精度 | 工具末端精度 ⭐ |
| 实际应用 | 不考虑工具 | 实际工作点 ⭐ |
| 训练难度 | 较容易 | 可能稍难（链更长） |
| 工作范围 | 较小 | 较大（工具长度） |
| 碰撞检测 | 不包括工具 | 包括工具 ⭐ |

## ✅ 检查清单

配置工具末端控制后：

- [x] 修改 `END_EFFECTOR_NAME = "endo360_needle"`
- [ ] 运行 `python test_star_env.py` 验证
- [ ] 启动可视化检查目标点位置
- [ ] 根据需要调整工作空间范围
- [ ] 根据需要调整方向约束
- [ ] 开始训练

## 🎓 总结

**当前配置**: 控制针尖 (`endo360_needle`)
- ✅ 适合实际应用
- ✅ 精确控制工具末端
- ✅ 符合你的需求

如果需要更改为其他末端执行器，只需修改配置文件中的 `END_EFFECTOR_NAME` 即可。

---

**配置时间**: 2025-10-29
**配置状态**: ✅ 已优化为工具末端控制

