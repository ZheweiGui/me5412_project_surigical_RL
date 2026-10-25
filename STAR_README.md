# STAR Robot Reach for Isaac Lab

本仓库在 Isaac Lab 上增加了 STAR 七轴机械臂与 Endo360 工具的末端位姿跟踪任务，并提供可直接用于推理的 RSL-RL checkpoint。

## 功能

- 机器人配置：7 个 `star_joint` 加 1 个 `endo360_joint`，共 8 维动作。
- 任务环境：`Isaac-Reach-Star-v0`（训练）和 `Isaac-Reach-Star-Play-v0`（评估）。
- 成功条件：针尖位置误差小于 1 cm，姿态误差小于 10°。
- 有界评估：支持固定 episode 数、随机种子、并行环境数及自定义阈值。
- 预训练模型：`checkpoints/star_reach/model_3800.pt`。

## 依赖

- Ubuntu 22.04
- Python 3.11
- Isaac Sim 5.0（Isaac Lab 主分支也支持兼容的 Isaac Sim 4.5 环境）
- RSL-RL
- NVIDIA GPU

先按上游 [Isaac Lab 安装文档](https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html) 完成环境配置，并安装本仓库扩展。

## STAR USD 资产

代码通过以下路径加载机器人资产：

```text
source/isaaclab_assets/isaaclab_assets/robots/star.usd
```

上游 Isaac Lab 的 `.gitignore` 默认排除 USD 文件，因此仓库不包含本地的 `star.usd`。运行前需将 STAR 资产放到上述路径。当前本地验证使用的资产大小为 28,460,558 字节。

## 快速评估

默认使用仓库内 checkpoint、1 个环境和 10 个 episode：

```bash
./play_with_success_rate.sh
```

最小 smoke eval：

```bash
./play_with_success_rate.sh --num_envs 1 --num_episodes 1
```

直接调用 Python 入口：

```bash
./isaaclab.sh -p scripts/play_with_metrics.py \
  --task Isaac-Reach-Star-Play-v0 \
  --checkpoint checkpoints/star_reach/model_3800.pt \
  --num_envs 1 \
  --num_episodes 10 \
  --seed 42 \
  --headless
```

可视化策略：

```bash
./play_star_reach.sh --visual
```

## 训练

```bash
./train_star_reach.sh --num_envs 20 --max_iterations 1000
```

训练输出保存在 `logs/rsl_rl/star_reach/`，该目录不会提交到 Git。

## Checkpoint

| 字段 | 值 |
| --- | --- |
| 文件 | `checkpoints/star_reach/model_3800.pt` |
| 大小 | 172,149 字节（约 168.1 KiB） |
| SHA-256 | `971562d5a1007b00e5e40fbe2fd5a111f1c257550b8ca822092467111f53b16b` |
| Actor | `31 → 64 → 64 → 8` |
| Critic | `31 → 64 → 64 → 1` |

`.pt` 文件由仓库现有 `.gitattributes` 使用 Git LFS 管理。克隆后如模型显示为文本指针，请先运行 `git lfs pull`。

## 验证记录

2026-10-25 使用 Isaac Sim 5.0、RTX 4090 D、固定种子 42、1 个环境完成了 2 个 episode 的 headless smoke eval：环境创建、checkpoint 加载、策略推理、指标统计和自动退出均成功，进程退出码为 0。这两个小样本的成功率为 0/2，仅用于验证代码链路，不代表 checkpoint 的正式性能；此前非固定种子的 9 个轻量 episode 中成功 1 次。

## 主要文件

```text
checkpoints/star_reach/model_3800.pt
scripts/play_with_metrics.py
source/isaaclab_assets/isaaclab_assets/robots/star.py
source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/config/star/
source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/reach/mdp/success_metrics.py
play_star_reach.sh
play_with_success_rate.sh
train_star_reach.sh
test_star_env.py
```

## 已知运行环境警告

本地测试中 Isaac Sim 报告重复 Vulkan ICD，以及 `endo360_calibrated`、`endo360_needle`、`star_link_ee` 和 `world` 的质量/惯量属性警告。这些警告未阻止环境创建或 checkpoint 推理，但正式实验前应清理显卡驱动 ICD，并修正 USD 中对应刚体的质量与惯量。
