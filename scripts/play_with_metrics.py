#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Evaluate a STAR reach checkpoint and report pose-tracking success."""

import argparse
import os
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

DEFAULT_CHECKPOINT = Path(__file__).resolve().parents[1] / "checkpoints" / "star_reach" / "model_3800.pt"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--disable_fabric", action="store_true", default=False, help="Disable Fabric and use USD I/O operations."
)
parser.add_argument("--num_envs", type=int, default=1, help="Number of parallel environments.")
parser.add_argument("--num_episodes", type=int, default=10, help="Stop after this many completed episodes.")
parser.add_argument("--task", type=str, default="Isaac-Reach-Star-Play-v0", help="Registered task name.")
parser.add_argument("--checkpoint", type=str, default=str(DEFAULT_CHECKPOINT), help="Checkpoint path.")
parser.add_argument("--seed", type=int, default=42, help="Environment seed.")
parser.add_argument("--print_interval", type=int, default=10, help="Metric print interval in simulation steps.")
parser.add_argument("--position_threshold", type=float, default=0.01, help="Success threshold in meters.")
parser.add_argument("--orientation_threshold", type=float, default=10.0, help="Success threshold in degrees.")
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.num_envs < 1:
    parser.error("--num_envs must be positive")
if args_cli.num_episodes < 1:
    parser.error("--num_episodes must be positive")
if args_cli.print_interval < 1:
    parser.error("--print_interval must be positive")

sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""The remaining imports require a running SimulationApp."""

import gymnasium as gym
import torch

from rsl_rl.runners import OnPolicyRunner

from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.utils.assets import retrieve_file_path
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude, quat_mul

from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlVecEnvWrapper

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils.hydra import hydra_task_config

END_EFFECTOR_BODY_NAME = "endo360_needle"


def _pose_errors(env) -> tuple[torch.Tensor, torch.Tensor]:
    """Return per-environment position and orientation errors in meters and radians."""
    robot = env.scene["robot"]
    command = env.command_manager.get_command("ee_pose")
    end_effector_index = robot.body_names.index(END_EFFECTOR_BODY_NAME)

    desired_position_body = command[:, :3]
    desired_position_world, _ = combine_frame_transforms(
        robot.data.root_pos_w, robot.data.root_quat_w, desired_position_body
    )
    current_position_world = robot.data.body_pos_w[:, end_effector_index]
    position_error = torch.linalg.vector_norm(current_position_world - desired_position_world, dim=1)

    desired_orientation_body = command[:, 3:7]
    desired_orientation_world = quat_mul(robot.data.root_quat_w, desired_orientation_body)
    current_orientation_world = robot.data.body_quat_w[:, end_effector_index]
    orientation_error = quat_error_magnitude(current_orientation_world, desired_orientation_world)

    return position_error, orientation_error


@hydra_task_config(args_cli.task, "rsl_rl_cfg_entry_point")
def main(env_cfg: ManagerBasedRLEnvCfg, agent_cfg: RslRlOnPolicyRunnerCfg) -> None:
    """Run a bounded evaluation and print aggregate success metrics."""
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.seed = args_cli.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    agent_cfg.seed = args_cli.seed

    checkpoint_path = retrieve_file_path(args_cli.checkpoint)
    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    print(f"[INFO] Experiment directory: {log_root_path}")
    print(f"[INFO] Loading checkpoint: {checkpoint_path}")

    env = None
    try:
        env = gym.make(args_cli.task, cfg=env_cfg)
        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
        runner.load(checkpoint_path)
        policy = runner.get_inference_policy(device=env.unwrapped.device)
        observations = env.get_observations()

        num_envs = env.unwrapped.num_envs
        successful_in_episode = torch.zeros(num_envs, dtype=torch.bool, device=env.unwrapped.device)
        completed_episodes = 0
        successful_episodes = 0
        timestep = 0
        orientation_threshold = torch.deg2rad(torch.tensor(args_cli.orientation_threshold, device=env.unwrapped.device))

        print("\n" + "=" * 80)
        print("STAR reach evaluation")
        print("=" * 80)
        print(f"Parallel environments: {num_envs}")
        print(f"Target episodes: {args_cli.num_episodes}")
        print(f"Maximum episode length: {env.unwrapped.max_episode_length} steps")
        print(f"Control time step: {env.unwrapped.step_dt:.4f} s")
        print(
            f"Success: position < {args_cli.position_threshold * 100:.2f} cm and "
            f"orientation < {args_cli.orientation_threshold:.2f} deg"
        )
        print("=" * 80)

        while simulation_app.is_running() and completed_episodes < args_cli.num_episodes:
            with torch.inference_mode():
                actions = policy(observations)
                observations, _, dones, _ = env.step(actions)
                dones = dones.bool()

                position_error, orientation_error = _pose_errors(env.unwrapped)
                success = (position_error < args_cli.position_threshold) & (orientation_error < orientation_threshold)
                # Isaac Lab auto-resets done environments during env.step(); their post-step
                # body state belongs to the next episode and must not enter the old metrics.
                successful_in_episode |= success & ~dones
                timestep += 1

                valid = ~dones
                if timestep % args_cli.print_interval == 0 and valid.any():
                    position_error_cm = position_error[valid].mean().item() * 100.0
                    orientation_error_deg = torch.rad2deg(orientation_error[valid]).mean().item()
                    print(
                        f"[step {timestep:5d}] active successes: {successful_in_episode.sum().item():3d}/{num_envs} | "
                        f"mean error: {position_error_cm:6.2f} cm, {orientation_error_deg:6.2f} deg"
                    )

                if dones.any():
                    done_successes = successful_in_episode[dones]
                    remaining_episodes = args_cli.num_episodes - completed_episodes
                    episodes_to_count = min(remaining_episodes, done_successes.numel())
                    successful_episodes += int(done_successes[:episodes_to_count].sum().item())
                    completed_episodes += episodes_to_count
                    successful_in_episode[dones] = False
                    print(
                        f"[episodes {completed_episodes:4d}/{args_cli.num_episodes}] "
                        f"success rate: {successful_episodes / completed_episodes * 100:6.2f}%"
                    )

        if completed_episodes:
            print("\n" + "=" * 80)
            print(
                f"Completed: {completed_episodes} episodes | successes: {successful_episodes} | "
                f"success rate: {successful_episodes / completed_episodes * 100:.2f}%"
            )
            print("=" * 80)
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Evaluation interrupted by user.")
    finally:
        simulation_app.close()
