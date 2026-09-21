#!/bin/bash
# Star Robot Reach 推理/演示脚本
# 使用方法: ./play_star_reach.sh [选项]

# 默认参数
NUM_ENVS=1000
RUN_NAME=""
CHECKPOINT=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --num_envs)
            NUM_ENVS="$2"
            shift 2
            ;;
        --run)
            RUN_NAME="$2"
            shift 2
            ;;
        --checkpoint)
            CHECKPOINT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "使用方法: $0 [--num_envs N] [--run RUN_NAME] [--checkpoint MODEL.pt]"
            exit 1
            ;;
    esac
done

echo "=================================================="
echo "Star Robot Reach 推理模式"
echo "=================================================="
echo "环境数量: $NUM_ENVS"

# 构建命令
CMD="./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs $NUM_ENVS"

# 添加 run name（如果指定）
if [ -n "$RUN_NAME" ]; then
    echo "运行: $RUN_NAME"
    CMD="$CMD --load_run $RUN_NAME"
else
    echo "运行: 自动检测最新"
fi

# 添加 checkpoint（如果指定）
if [ -n "$CHECKPOINT" ]; then
    echo "Checkpoint: $CHECKPOINT"
    CMD="$CMD --checkpoint $CHECKPOINT"
else
    echo "Checkpoint: 自动使用最新"
fi

echo "=================================================="
echo ""

# 运行
eval $CMD

echo ""
echo "=================================================="
echo "推理完成"
echo "=================================================="

