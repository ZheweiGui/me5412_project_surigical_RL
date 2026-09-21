# Star Robot 快速 Play 指南

## 🎮 快速开始

### 方法 1: 使用便捷脚本（推荐）

```bash
# 使用默认设置（1000 个环境，自动找最新模型）
./play_star_reach.sh

# 指定运行和 checkpoint
./play_star_reach.sh --run 2025-10-29_14-37-12 --checkpoint model_3800.pt

# 使用少量环境（更快）
./play_star_reach.sh --num_envs 32
```

### 方法 2: 直接命令

```bash
# 使用最新训练的模型
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32

# 指定具体的训练运行
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --load_run 2025-10-29_14-37-12

# 指定具体的 checkpoint
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --load_run 2025-10-29_14-37-12 \
    --checkpoint model_3800.pt
```

## 📁 你的训练记录

**位置**: `logs/rsl_rl/star_reach/2025-10-29_14-37-12/`

**可用的 checkpoint**:
- `model_50.pt` - 早期（50 次迭代）
- `model_100.pt` - 100 次迭代
- ...
- `model_3800.pt` - 最新（3800 次迭代） ⭐

**推荐使用**: `model_3800.pt`（最新训练的模型）

## 🎯 参数说明

### `--num_envs`
- **默认**: 1000（你的修改）
- **推荐**: 32-256
- **说明**: 
  - 少量环境（32）: 更流畅的可视化
  - 大量环境（1000+）: 用于评估性能

### `--load_run`
- **格式**: 时间戳文件夹名
- **例子**: `2025-10-29_14-37-12`
- **说明**: 指定使用哪次训练的结果
- **省略**: 自动使用最新的训练

### `--checkpoint`
- **格式**: 模型文件名
- **例子**: `model_3800.pt`
- **说明**: 指定使用哪个 checkpoint
- **省略**: 自动使用该运行中最新的 checkpoint

## 🖥️ 可视化选项

### 查看训练过程（可视化）

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --load_run 2025-10-29_14-37-12
```

这会打开 Isaac Sim 窗口，显示机器人执行任务。

### 无头模式（评估性能）

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 1000 \
    --load_run 2025-10-29_14-37-12 \
    --headless
```

更快，用于评估平均奖励。

## 📊 评估指标

运行 play 时，会显示：

```
Episode Reward Mean: 0.XX        # 平均奖励
Episode Reward Std: 0.XX         # 奖励标准差
Episode Length Mean: XXX         # 平均 episode 长度
Success Rate: XX%                # 成功率（如果有定义）
```

## 🔍 观察要点

在可视化窗口中观察：

1. **目标点**（红色球体）
   - 每 4 秒重新采样
   - 机器人应该尝试到达它

2. **针尖运动**
   - 应该平滑接近目标
   - 无剧烈抖动

3. **工作空间**
   - X: 35-65 cm（前方）
   - Y: ±20 cm（左右）
   - Z: 15-50 cm（高度）

4. **行为质量**
   - 是否能快速接近目标？
   - 运动是否平滑？
   - 是否能保持方向？

## 📈 比较不同 checkpoint

### 比较早期 vs 后期模型

```bash
# 早期模型（100 次迭代）
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --checkpoint model_100.pt

# 后期模型（3800 次迭代）
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --checkpoint model_3800.pt
```

观察：
- 早期：可能运动不稳定，难以到达目标
- 后期：应该平滑、准确地到达目标

## ⚠️ 常见问题

### 问题 1: "No runs present in the directory"

**原因**: 指定的运行不存在

**解决方案**:
```bash
# 查看可用的运行
ls logs/rsl_rl/star_reach/

# 使用正确的运行名
./play_star_reach.sh --run 2025-10-29_14-37-12
```

### 问题 2: "Checkpoint not found"

**原因**: 指定的 checkpoint 文件不存在

**解决方案**:
```bash
# 查看可用的 checkpoint
ls logs/rsl_rl/star_reach/2025-10-29_14-37-12/model_*.pt

# 使用存在的 checkpoint
./play_star_reach.sh --checkpoint model_3800.pt
```

### 问题 3: 模型表现很差

**可能原因**:
- 使用了早期的 checkpoint
- 训练不充分
- 配置参数变化导致不兼容

**解决方案**:
- 使用最新的 checkpoint
- 继续训练
- 确保 play 时的配置与训练时一致

## 🎯 推荐工作流

### 1. 快速查看（少量环境）
```bash
./play_star_reach.sh --num_envs 32
```

### 2. 性能评估（大量环境）
```bash
./play_star_reach.sh --num_envs 1000 --headless
```

### 3. 比较不同阶段
```bash
# 中期
./play_star_reach.sh --checkpoint model_1000.pt --num_envs 32

# 后期
./play_star_reach.sh --checkpoint model_3800.pt --num_envs 32
```

## 📝 命令速查表

| 场景 | 命令 |
|------|------|
| **默认运行** | `./play_star_reach.sh` |
| **指定环境数** | `./play_star_reach.sh --num_envs 32` |
| **指定运行** | `./play_star_reach.sh --run 2025-10-29_14-37-12` |
| **指定模型** | `./play_star_reach.sh --checkpoint model_3800.pt` |
| **完整指定** | `./play_star_reach.sh --run 2025-10-29_14-37-12 --checkpoint model_3800.pt --num_envs 32` |

## 🎬 录制视频（可选）

如果想录制演示视频：

```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 1 \
    --load_run 2025-10-29_14-37-12 \
    --video \
    --video_length 200
```

视频会保存在日志目录中。

---

**快速开始**: 直接运行 `./play_star_reach.sh` 即可！

