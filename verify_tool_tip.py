#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Inspect STAR tool-tip bodies and their world positions."""

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--task", type=str, default="Isaac-Reach-Star-Play-v0", help="Registered task name.")
parser.add_argument("--num_steps", type=int, default=10, help="Number of zero-action simulation steps.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""The remaining imports require a running SimulationApp."""

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg

BODIES_TO_CHECK = (
    "star_link_ee",
    "ati",
    "endo360_link_1",
    "endo360_needle",
    "endo360_calibrated",
)


def main() -> None:
    """Create one environment and report the configured tool-tip geometry."""
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=1)
    env = gym.make(args_cli.task, cfg=env_cfg)

    try:
        env.reset()
        robot = env.unwrapped.scene["robot"]

        print("Available bodies:")
        for index, body_name in enumerate(robot.body_names):
            print(f"  [{index:2d}] {body_name}")

        positions = {}
        print("\nSelected body positions:")
        for body_name in BODIES_TO_CHECK:
            body_indices, _ = robot.find_bodies(body_name)
            if not body_indices:
                print(f"  {body_name}: not found")
                continue
            body_index = body_indices[0]
            position = robot.data.body_pos_w[0, body_index].detach().cpu()
            positions[body_name] = position
            print(f"  {body_name}: [{position[0]:.4f}, {position[1]:.4f}, {position[2]:.4f}] m")

        if "star_link_ee" in positions and "endo360_needle" in positions:
            offset = positions["endo360_needle"] - positions["star_link_ee"]
            print("\nFlange-to-needle offset:")
            print(f"  xyz: [{offset[0]:.4f}, {offset[1]:.4f}, {offset[2]:.4f}] m")
            print(f"  length: {torch.linalg.vector_norm(offset).item() * 1000.0:.1f} mm")

        print(f"\nConfigured command body: {env.unwrapped.cfg.commands.ee_pose.body_name}")

        for _ in range(args_cli.num_steps):
            actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
            env.step(actions)
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
