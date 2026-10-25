#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
num_envs=20
max_iterations=1000
headless=true

usage() {
    echo "Usage: $0 [--num_envs N] [--max_iterations N] [--visual]"
}

while (($#)); do
    case "$1" in
        --num_envs)
            num_envs=${2:?"--num_envs requires a value"}
            shift 2
            ;;
        --max_iterations)
            max_iterations=${2:?"--max_iterations requires a value"}
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
    "$script_dir/isaaclab.sh" -p "$script_dir/scripts/reinforcement_learning/rsl_rl/train.py"
    --task Isaac-Reach-Star-v0
    --num_envs "$num_envs"
    --max_iterations "$max_iterations"
)
if [[ $headless == true ]]; then
    command+=(--headless)
fi

"${command[@]}"
