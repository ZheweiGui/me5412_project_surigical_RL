# Star Robot Reach 环境 - 快速开始

## 🎯 概述

已为你的 `star.usd` 机器人创建了一个类似 `Isaac-Reach-Franka-v0` 的强化学习环境。

**新环境名称**: `Isaac-Reach-Star-v0`

## 🚀 快速开始（3 步）

### 步骤 1: 检查 USD 文件结构

```bash
python inspect_star_usd.py
```

这个脚本会：
- ✅ 列出所有关节名称
- ✅ 列出所有 body/link 名称  
- ✅ 生成配置建议

### 步骤 2: 更新配置文件

根据 `inspect_star_usd.py` 的输出，更新以下文件：

**A. 机器人配置** - `source/isaaclab_assets/isaaclab_assets/robots/star.py`
- 设置正确的关节名称和初始位置
- 配置执行器参数

**B. 环境配置** - `source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py`
- 设置末端执行器名称（`END_EFFECTOR_NAME`）
- 设置关节控制模式

### 步骤 3: 测试和训练

```bash
# 测试环境
python test_star_env.py

# 如果测试通过，开始训练
./train_star_reach.sh

# 或使用自定义参数
./train_star_reach.sh --num_envs 2048 --visual
```

## 📁 创建的文件

```
IsaacLab/
├── source/
│   ├── isaaclab_assets/isaaclab_assets/robots/
│   │   └── star.py                           # 机器人资产配置 ⚙️
│   │
│   └── isaaclab_tasks/.../reach/config/star/
│       ├── __init__.py                       # 环境注册 📝
│       ├── joint_pos_env_cfg.py             # 环境配置 🎮
│       └── agents/
│           ├── __init__.py
│           └── rsl_rl_ppo_cfg.py           # PPO 算法配置 🧠
│
├── inspect_star_usd.py                       # USD 检查工具 🔍
├── test_star_env.py                          # 环境测试脚本 ✅
├── train_star_reach.sh                       # 训练启动脚本 🚀
├── STAR_README.md                            # 本文件 📖
└── STAR_ROBOT_SETUP_GUIDE.md                # 详细指南 📚
```

## 🎓 训练命令

### 基础训练
```bash
./train_star_reach.sh
```

### 带可视化
```bash
./train_star_reach.sh --visual
```

### 自定义参数
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Reach-Star-v0 \
    --num_envs 4096 \
    --headless
```

### 查看训练结果
```bash
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs 32 \
    --load_run <运行文件夹>
```

## 🔧 需要配置的关键参数

### 在 `star.py` 中：
- ✏️ 关节名称（`joint_pos`）
- ✏️ 执行器配置（`actuators`）

### 在 `joint_pos_env_cfg.py` 中：
- ✏️ 末端执行器名称（`END_EFFECTOR_NAME`）
- ✏️ 关节名称模式（`joint_names`）

## ❓ 遇到问题？

### 环境无法加载
1. 检查 `star.usd` 是否在正确位置
2. 运行 `python inspect_star_usd.py` 检查文件结构

### 关节控制不工作
1. 确认关节名称与 USD 文件匹配
2. 检查 `actuators` 配置中的 `joint_names_expr`

### 训练不稳定
1. 调整执行器的 `stiffness` 和 `damping`
2. 检查初始关节位置是否合理
3. 调整 PPO 超参数

## 📚 更多帮助

- **详细配置指南**: 查看 `STAR_ROBOT_SETUP_GUIDE.md`
- **环境测试**: 运行 `python test_star_env.py`
- **USD 检查**: 运行 `python inspect_star_usd.py`

## ✅ 配置检查清单

- [ ] 运行 `inspect_star_usd.py` 并记录关节信息
- [ ] 更新 `star.py` 中的关节配置
- [ ] 更新 `joint_pos_env_cfg.py` 中的末端执行器名称
- [ ] 运行 `test_star_env.py` 确认环境正常
- [ ] 开始训练！

---

**祝训练顺利！** 🎉

如有问题，请查看 `STAR_ROBOT_SETUP_GUIDE.md` 获取详细说明。

