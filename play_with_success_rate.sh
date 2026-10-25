#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
num_envs=1
num_episodes=10
checkpoint="$script_dir/checkpoints/star_reach/model_3800.pt"
headless=true

usage() {
    echo "Usage: $0 [--num_envs N] [--num_episodes N] [--checkpoint MODEL.pt] [--visual]"
}

while (($#)); do
    case "$1" in
        --num_envs)
            num_envs=${2:?"--num_envs requires a value"}
            shift 2
            ;;
        --num_episodes)
            num_episodes=${2:?"--num_episodes requires a value"}
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
    "$script_dir/isaaclab.sh" -p "$script_dir/scripts/play_with_metrics.py"
    --task Isaac-Reach-Star-Play-v0
    --num_envs "$num_envs"
    --num_episodes "$num_episodes"
    --checkpoint "$checkpoint"
)
if [[ $headless == true ]]; then
    command+=(--headless)
fi

printf 'Running STAR evaluation with %s environment(s) for %s episode(s).\n' "$num_envs" "$num_episodes"
"${command[@]}"
