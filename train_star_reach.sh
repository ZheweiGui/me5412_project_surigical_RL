#!/bin/bash
# Star Robot Reach 训练脚本
# 使用方法: ./train_star_reach.sh [选项]

# 默认参数
NUM_ENVS=20
HEADLESS="--headless"
MAX_ITERATIONS=1000000

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --visual)
            HEADLESS=""
            shift
            ;;
        --num_envs)
            NUM_ENVS="$2"
            shift 2
            ;;
        --max_iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "使用方法: $0 [--visual] [--num_envs N] [--max_iterations N]"
            exit 1
            ;;
    esac
done

echo "=================================================="
echo "Star Robot Reach 环境训练"
echo "=================================================="
echo "环境数量: $NUM_ENVS"
echo "最大迭代: $MAX_ITERATIONS"
echo "可视化模式: $([ -z "$HEADLESS" ] && echo "开启" || echo "关闭")"
echo "=================================================="
echo ""

# 运行训练
./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Reach-Star-v0 \
    --num_envs $NUM_ENVS \
    --max_iterations $MAX_ITERATIONS

echo ""
echo "训练完成！"
echo ""
echo "要查看训练结果，运行:"
echo "./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/play.py \\"
echo "    --task Isaac-Reach-Star-Play-v0 \\"
echo "    --num_envs 32 \\"
echo "    --load_run <运行文件夹名称>"

