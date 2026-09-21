#!/bin/bash
# Star Robot Reach Play 脚本（带成功率统计）
# 使用方法: ./play_with_success_rate.sh [选项]

# 默认参数
NUM_ENVS=1000
RUN_NAME="2025-10-29_14-37-12"
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
echo "Star Robot Reach 推理模式 (带成功率统计)"
echo "=================================================="
echo "环境数量: $NUM_ENVS"
echo "运行: $RUN_NAME"
if [ -n "$CHECKPOINT" ]; then
    echo "Checkpoint: $CHECKPOINT"
else
    echo "Checkpoint: 自动使用最新"
fi
echo ""
echo "成功判断标准:"
echo "  - 位置误差 < 1cm"
echo "  - 方向误差 < 10 degrees"
echo "=================================================="
echo ""

# 构建命令
CMD="./isaaclab.sh -p scripts/play_with_metrics.py \
    --task Isaac-Reach-Star-Play-v0 \
    --num_envs $NUM_ENVS"

# 添加 checkpoint（如果指定）
if [ -n "$CHECKPOINT" ]; then
    CMD="$CMD load_run=$RUN_NAME load_checkpoint=$CHECKPOINT"
else
    CMD="$CMD load_run=$RUN_NAME"
fi

# 运行
eval $CMD

echo ""
echo "=================================================="
echo "评估完成"
echo "=================================================="

