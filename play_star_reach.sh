#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
num_envs=1
checkpoint="$script_dir/checkpoints/star_reach/model_3800.pt"
headless=true

usage() {
    echo "Usage: $0 [--num_envs N] [--checkpoint MODEL.pt] [--visual]"
}

while (($#)); do
    case "$1" in
        --num_envs)
            num_envs=${2:?"--num_envs requires a value"}
            shift 2
            ;;
        --checkpoint)
            checkpoint=${2:?"--checkpoint requires a value"}
            shift 2
            ;;
        --visual)
            headless=false
            shift
            ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

command=(
    "$script_dir/isaaclab.sh" -p "$script_dir/scripts/reinforcement_learning/rsl_rl/play.py"
    --task Isaac-Reach-Star-Play-v0
    --num_envs "$num_envs"
    --checkpoint "$checkpoint"
)
if [[ $headless == true ]]; then
    command+=(--headless)
fi

"${command[@]}"
