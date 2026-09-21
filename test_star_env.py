#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""测试 Star Reach 环境是否正确配置和加载

运行此脚本来验证环境设置：
    python test_star_env.py
"""

import gymnasium as gym
import torch

# 导入 isaaclab_tasks 来注册环境
import isaaclab_tasks  # noqa: F401


def test_star_reach_env():
    """测试 Star Reach 环境"""
    print("=" * 80)
    print("测试 Star Reach 环境")
    print("=" * 80)
    
    try:
        # 尝试创建环境
        print("\n1. 正在创建环境: Isaac-Reach-Star-v0")
        env = gym.make("Isaac-Reach-Star-v0", num_envs=2, headless=True)
        print("✓ 环境创建成功！")
        
        # 重置环境
        print("\n2. 正在重置环境...")
        obs, _ = env.reset()
        print(f"✓ 环境重置成功！")
        print(f"   观察空间维度: {obs['policy'].shape}")
        
        # 执行几步
        print("\n3. 正在执行测试步骤...")
        for i in range(5):
            # 随机动作
            action = 2.0 * torch.rand(env.action_space.shape, device=env.unwrapped.device) - 1.0
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"   步骤 {i+1}: reward = {reward.mean().item():.4f}")
        
        print("\n✓ 所有测试通过！")
        print("\n环境信息:")
        print(f"   - 观察空间: {obs['policy'].shape}")
        print(f"   - 动作空间: {env.action_space.shape}")
        print(f"   - 环境数量: {env.unwrapped.num_envs}")
        
        # 关闭环境
        env.close()
        print("\n环境已正确关闭")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        print("\n可能的问题:")
        print("1. star.usd 文件路径不正确")
        print("2. 机器人关节名称配置不正确")
        print("3. 末端执行器名称配置不正确")
        print("\n请检查以下文件的配置:")
        print("   - source/isaaclab_assets/isaaclab_assets/robots/star.py")
        print("   - source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py")
        return False


if __name__ == "__main__":
    success = test_star_reach_env()
    exit(0 if success else 1)

