#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Script to play a checkpoint with additional metrics including success rate.

This script extends the standard play script to include:
- Success rate calculation (position < 1cm AND orientation < 10 degrees)
- Position error statistics (in cm)
- Orientation error statistics (in degrees)
- Episode-level metrics
"""

import argparse
import sys
import torch

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Play a checkpoint of an RL agent with success metrics.")
parser.add_argument(
    "--disable_fabric", action="store_true", default=False, help="Disable fabric and use USD I/O operations."
)
parser.add_argument("--num_envs", type=int, default=None, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint.")
# append AppLauncher cli args (includes --cpu, --device, etc.)
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli, hydra_args = parser.parse_known_args()

# clear out sys.argv for Hydra
sys.argv = [sys.argv[0]] + hydra_args

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
import numpy as np
import os

from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude, quat_mul
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import isaaclab_tasks  # noqa: F401


@hydra_task_config(args_cli.task, "rsl_rl_cfg_entry_point")
def main(env_cfg: ManagerBasedRLEnvCfg, agent_cfg: RslRlOnPolicyRunnerCfg):
    """Play with an RL agent and compute success metrics."""
    
    # override configurations with non-hydra CLI arguments
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    
    # create isaac environment
    env = gym.make(args_cli.task, cfg=env_cfg)
    
    # specify directory for logging experiments
    log_root_path = os.path.join("logs", "rsl_rl", agent_cfg.experiment_name)
    log_root_path = os.path.abspath(log_root_path)
    print(f"[INFO] Loading experiment from directory: {log_root_path}")
    
    if args_cli.checkpoint:
        resume_path = args_cli.checkpoint
    else:
        resume_path = get_checkpoint_path(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)
    print(f"[INFO]: Loading model checkpoint from: {resume_path}")
    
    # wrap environment for rsl-rl
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
    env = RslRlVecEnvWrapper(env)
    
    # load previously trained model
    from rsl_rl.runners import OnPolicyRunner
    ppo_runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    ppo_runner.load(resume_path)
    print("[INFO]: Loading model from checkpoint successful!")
    
    # obtain the trained policy for inference
    policy = ppo_runner.get_inference_policy(device=env.unwrapped.device)
    
    # reset environment
    obs = env.get_observations()
    
    # Metrics tracking for batch evaluation
    batch_count = 0  # 批次计数
    num_envs = env.unwrapped.num_envs
    
    # Track if each environment has achieved success at least once in current batch
    batch_successes = torch.zeros(num_envs, dtype=torch.bool, device=env.unwrapped.device)
    
    # Statistics
    all_success_rates = []
    all_success_counts = []
    
    # simulate environment
    timestep = 0
    steps_in_batch = 0
    
    print("\n" + "=" * 80)
    print("开始评估（批量成功率统计）")
    print("=" * 80)
    print(f"环境信息:")
    print(f"  - 并行环境数量: {num_envs}")
    print(f"  - 最大 Episode 长度: {env.unwrapped.max_episode_length} 步")
    print(f"  - 物理时间步: {env.unwrapped.physics_dt:.4f}s")
    print(f"  - Decimation: {env.unwrapped.cfg.decimation}")
    print(f"  - 控制时间步: {env.unwrapped.step_dt:.4f}s")
    print(f"\n成功判断标准:")
    print(f"  - 位置误差 < 1cm")
    print(f"  - 旋转误差 < 10 degrees")
    print(f"\n统计方式: 每次所有{num_envs}个环境一起reset，统计其中成功的数量")
    print("=" * 80)
    print("\n按 Ctrl+C 停止评估...\n")
    
    while simulation_app.is_running():
        with torch.inference_mode():
            # agent stepping
            actions = policy(obs)
            # env stepping
            obs, _, dones, info = env.step(actions)
            
            steps_in_batch += 1
            
            # 手动计算成功条件（因为 Play 模式禁用了 success termination）
            # 成功条件: 位置误差 < 1cm (0.01m) 且 旋转误差 < 10度 (0.1745 rad)
            unwrapped_env = env.unwrapped
            
            # 获取当前末端执行器位置和目标位置
            robot = unwrapped_env.scene["robot"]
            command = unwrapped_env.command_manager.get_command("ee_pose")
            
            # 目标位置（body frame）
            des_pos_b = command[:, :3]
            des_pos_w, _ = combine_frame_transforms(robot.data.root_pos_w, robot.data.root_quat_w, des_pos_b)
            
            # 当前末端位置（world frame）- 使用 endo360_needle
            body_names = robot.body_names
            ee_body_idx = body_names.index("endo360_needle")
            curr_pos_w = robot.data.body_pos_w[:, ee_body_idx]
            
            # 位置误差
            position_error = torch.norm(curr_pos_w - des_pos_w, dim=1)
            
            # 计算旋转误差
            des_quat_b = command[:, 3:7]
            des_quat_w = quat_mul(robot.data.root_quat_w, des_quat_b)
            curr_quat_w = robot.data.body_quat_w[:, ee_body_idx]
            orientation_error = quat_error_magnitude(curr_quat_w, des_quat_w)
            
            # 成功判断
            position_threshold = 0.01  # 1cm
            orientation_threshold = 0.1745  # 10 degrees in radians
            success_this_step = (position_error < position_threshold) & (orientation_error < orientation_threshold)
            
            # Mark which environments have achieved success at least once
            batch_successes |= success_this_step.bool()
            
            # 统计当前批次的累计成功数
            current_success_count = batch_successes.sum().item()
            current_success_rate = (current_success_count / num_envs) * 100
            
            # 计算平均误差
            avg_pos_err = position_error.mean().item() * 100  # cm
            avg_rot_err = torch.rad2deg(orientation_error.mean()).item()  # degrees
            
            # 每10步打印一次统计
            if steps_in_batch % 10 == 0:
                print(f"[批次{batch_count+1} 步{steps_in_batch:4d}] "
                      f"累计成功: {current_success_count:3d}/{num_envs} ({current_success_rate:5.1f}%) | "
                      f"平均误差: 位置 {avg_pos_err:5.2f}cm 旋转 {avg_rot_err:5.1f}°")
            
            # Check if any environment is done (all will reset together)
            if dones.any():
                # 统计这一批次的成功情况
                batch_count += 1
                success_count = batch_successes.sum().item()
                success_rate = (success_count / num_envs) * 100
                
                # 保存统计
                all_success_counts.append(success_count)
                all_success_rates.append(success_rate)
                
                # 打印这一批次的结果
                print(f"[批次 {batch_count:3d}] 成功: {success_count:3d}/{num_envs} ({success_rate:5.1f}%) | "
                      f"步数: {steps_in_batch:4d} | "
                      f"累计平均SR: {sum(all_success_rates)/len(all_success_rates):5.1f}%")
                
                # 重置批次追踪器
                batch_successes.zero_()
                steps_in_batch = 0
        
        timestep += 1
    
    # Final statistics
    print("\n" + "=" * 80)
    print("评估完成！")
    print("=" * 80)
    print(f"总批次数: {batch_count}")
    print(f"每批环境数: {num_envs}")
    print(f"总评估次数: {batch_count * num_envs}")
    
    if all_success_rates:
        avg_sr = sum(all_success_rates) / len(all_success_rates)
        min_sr = min(all_success_rates)
        max_sr = max(all_success_rates)
        total_successes = sum(all_success_counts)
        total_trials = batch_count * num_envs
        
        print(f"\n总体成功率: {total_successes}/{total_trials} = {(total_successes/total_trials)*100:.2f}%")
        print(f"\n批次级别统计:")
        print(f"  - 平均成功率: {avg_sr:.2f}%")
        print(f"  - 最低成功率: {min_sr:.2f}%")
        print(f"  - 最高成功率: {max_sr:.2f}%")
    else:
        print("没有完成任何批次")
    print("=" * 80)
    
    # Close the simulator
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()

