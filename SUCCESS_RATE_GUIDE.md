# Star Robot 成功率评估指南

## 🎯 功能说明

现在 Play 模式会额外输出**成功率（Success Rate）**，判断标准为：

✅ **成功条件**:
- **位置误差** < 1cm (0.01m)
- **方向误差** < 10° (0.1745 弧度)

两个条件**同时满足**才算成功。

## 📁 已添加的文件

### 1. 成功判断函数
**文件**: `source/isaaclab_tasks/.../reach/mdp/success_metrics.py`

包含三个函数：
- `is_success()` - 判断是否成功（返回 0 或 1）
- `position_error_cm()` - 位置误差（cm）
- `orientation_error_deg()` - 方向误差（度）

### 2. 环境配置更新
**文件**: `source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`

添加了成功判断的 termination term：
```python
self.terminations.success = DoneTerm(
    func=mdp.is_success,
    params={
        "command_name": "ee_pose",
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "position_threshold": 0.01,  # 1cm
        "orientation_threshold": 0.1745,  # 10 degrees
    },
)
```

### 3. 带成功率的 Play 脚本
**文件**: `scripts/play_with_metrics.py`

增强版 play 脚本，会自动计算和显示成功率。

### 4. 便捷启动脚本
**文件**: `play_with_success_rate.sh`

快速启动带成功率统计的 play。

## 🚀 使用方法

### 方法 1: 使用便捷脚本（推荐）

```bash
# 基本用法（使用默认配置）
./play_with_success_rate.sh

# 指定环境数量
./play_with_success_rate.sh --num_envs 100

# 指定运行和 checkpoint
./play_with_success_rate.sh --run 2025-10-29_14-37-12 --checkpoint model_3800.pt
```

### 方法 2: 直接使用脚本

```bash
./isaaclab.sh -p scripts/play_with_metrics.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 100 \
    load_run=2025-10-29_14-37-12
```

## 📊 输出示例

运行时会看到类似这样的输出：

```
================================================================================
Starting evaluation with success rate tracking...
================================================================================
Success criteria:
  - Position error < 1cm
  - Orientation error < 10 degrees
================================================================================

[Step 100] Episodes: 25, Success Rate: 72.00%
[Step 200] Episodes: 50, Success Rate: 76.00%
[Step 300] Episodes: 75, Success Rate: 74.67%

================================================================================
Evaluation Complete!
================================================================================
Total Episodes: 100
Successful Episodes: 75
Success Rate: 75.00%
================================================================================
```

## 🔢 成功判断逻辑

### 位置误差计算

```python
# 获取目标位置和当前位置
des_pos = command[:, :3]  # 目标位置 (x, y, z)
curr_pos = body_pos_w     # 当前末端位置

# 计算欧式距离
position_error = ||curr_pos - des_pos||  # 米

# 判断
position_success = (position_error < 0.01)  # 1cm
```

### 方向误差计算

```python
# 获取目标方向和当前方向（四元数）
des_quat = command[:, 3:7]   # 目标方向
curr_quat = body_quat_w      # 当前方向

# 计算四元数角度误差
orientation_error = quat_error_magnitude(curr_quat, des_quat)  # 弧度

# 判断
orientation_success = (orientation_error < 0.1745)  # 10度
```

### 总体判断

```python
success = position_success AND orientation_success
```

## 📈 评估策略

### 快速评估（推荐开始时使用）

```bash
# 少量环境，快速查看
./play_with_success_rate.sh --num_envs 32
```

**优点**:
- 快速得到初步结果
- 可以可视化观察

### 详细评估（推荐最终评估）

```bash
# 大量环境，统计更准确
./play_with_success_rate.sh --num_envs 500
```

**优点**:
- 统计更可靠
- 减少随机性影响

### 不同阶段对比

```bash
# 评估早期模型
./play_with_success_rate.sh --checkpoint model_500.pt --num_envs 100

# 评估中期模型
./play_with_success_rate.sh --checkpoint model_2000.pt --num_envs 100

# 评估最终模型
./play_with_success_rate.sh --checkpoint model_3800.pt --num_envs 100
```

## 📊 成功率分析

### 理想成功率

| 训练进度 | 预期成功率 | 说明 |
|---------|-----------|------|
| 早期（< 500 iter） | 0-30% | 刚开始学习 |
| 中期（500-2000 iter） | 30-60% | 逐步改善 |
| 后期（2000-4000 iter） | 60-90% | 接近最优 |
| 充分训练（> 4000 iter） | 70-95% | 性能良好 |

### 影响因素

成功率受以下因素影响：

1. **训练充分程度**
   - 训练时间越长，成功率通常越高

2. **工作空间大小**
   - 当前: X: 35-65cm, Y: ±20cm, Z: 15-50cm
   - 范围越大，任务越难

3. **成功阈值**
   - 当前: 1cm + 10°
   - 阈值越严格，成功率越低

4. **PD 参数**
   - 影响控制精度和稳定性

## 🔧 调整成功标准

如果你想修改成功判断标准，编辑配置文件：

`source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`

### 示例：更严格的标准

```python
self.terminations.success = DoneTerm(
    func=mdp.is_success,
    params={
        "command_name": "ee_pose",
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "position_threshold": 0.005,  # 5mm（更严格）
        "orientation_threshold": 0.0873,  # 5度（更严格）
    },
)
```

### 示例：更宽松的标准

```python
self.terminations.success = DoneTerm(
    func=mdp.is_success,
    params={
        "command_name": "ee_pose",
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "position_threshold": 0.02,  # 2cm（更宽松）
        "orientation_threshold": 0.349,  # 20度（更宽松）
    },
)
```

### 示例：只考虑位置

```python
self.terminations.success = DoneTerm(
    func=mdp.is_success,
    params={
        "command_name": "ee_pose",
        "asset_cfg": SceneEntityCfg("robot", body_names=["endo360_needle"]),
        "position_threshold": 0.01,  # 1cm
        "orientation_threshold": 10.0,  # 实际上忽略方向（10弧度 ≈ 573度）
    },
)
```

## 💡 使用技巧

### 1. 批量评估不同 checkpoint

创建一个脚本来自动评估所有 checkpoint：

```bash
#!/bin/bash
for ckpt in 1000 2000 3000 3800; do
    echo "Evaluating model_${ckpt}.pt..."
    ./play_with_success_rate.sh \
        --checkpoint model_${ckpt}.pt \
        --num_envs 200 \
        2>&1 | tee eval_${ckpt}.log
done
```

### 2. 记录评估结果

```bash
# 将输出保存到文件
./play_with_success_rate.sh --num_envs 200 | tee evaluation_results.txt
```

### 3. 可视化观察失败案例

```bash
# 使用少量环境，便于观察
./play_with_success_rate.sh --num_envs 4
```

然后在可视化窗口中观察：
- 哪些目标位置难以到达？
- 失败时的典型行为是什么？
- 位置误差还是方向误差更大？

## 🎯 与标准 Play 的对比

| 特性 | 标准 play.py | play_with_metrics.py |
|------|-------------|---------------------|
| **基本功能** | ✅ | ✅ |
| **可视化** | ✅ | ✅ |
| **成功率统计** | ❌ | ✅ |
| **实时更新** | ❌ | ✅ |
| **Episode 统计** | ✅ | ✅ |
| **额外指标** | ❌ | ✅ |

## ⚠️ 注意事项

### 1. Episode 长度

- 默认 episode 长度: 12 秒
- 如果机器人未在 episode 内达到目标，不算成功
- 成功后 episode 不会立即结束（会继续到时间限制）

### 2. 多次成功

- 一个 episode 中可能多次达到成功状态
- 只要至少成功一次，该 episode 就计为成功

### 3. 评估环境数

- 环境数越多，统计越准确
- 但会增加评估时间
- 推荐: 100-500 个环境

## 📝 快速命令参考

```bash
# 快速评估（32 环境）
./play_with_success_rate.sh

# 详细评估（200 环境）
./play_with_success_rate.sh --num_envs 200

# 指定模型
./play_with_success_rate.sh --checkpoint model_3800.pt --num_envs 100

# 无头模式（更快，无可视化）
./isaaclab.sh -p scripts/play_with_metrics.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 500 \
    --headless \
    load_run=2025-10-29_14-37-12
```

---

**成功标准**: 位置 < 1cm AND 方向 < 10°  
**快速开始**: `./play_with_success_rate.sh`  
**推荐评估**: 100-200 个环境

