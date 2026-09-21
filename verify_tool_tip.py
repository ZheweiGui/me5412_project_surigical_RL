#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""验证工具末端执行器位置

这个脚本会创建环境并显示：
1. 可用的所有 body 名称
2. 当前配置的末端执行器位置
3. 工具链的相对位置关系

运行: python verify_tool_tip.py
"""

import gymnasium as gym
import torch

# 导入 isaaclab_tasks 来注册环境
import isaaclab_tasks  # noqa: F401


def verify_tool_tip():
    """验证工具末端执行器配置"""
    print("=" * 80)
    print("验证 Star Robot 工具末端配置")
    print("=" * 80)
    
    try:
        # 创建环境（单个环境用于调试）
        print("\n1. 正在创建环境...")
        env = gym.make("Isaac-Reach-Star-v0", num_envs=1, headless=False)
        env.reset()
        print("✓ 环境创建成功\n")
        
        # 获取机器人
        robot = env.unwrapped.scene["robot"]
        
        # 显示所有 body
        print("=" * 80)
        print("📦 可用的 Body/Link 列表:")
        print("=" * 80)
        for idx, body_name in enumerate(robot.data.body_names):
            print(f"  [{idx:2d}] {body_name}")
        
        # 获取关键位置
        print("\n" + "=" * 80)
        print("📍 关键位置信息:")
        print("=" * 80)
        
        bodies_to_check = [
            "star_link_ee",      # 机械臂末端
            "ati",               # 力传感器
            "endo360_link_1",    # 工具链接
            "endo360_needle",    # 针尖
            "endo360_calibrated" # 校准点
        ]
        
        positions = {}
        for body_name in bodies_to_check:
            try:
                body_idx = robot.find_bodies(body_name)[0][0]
                pos = robot.data.body_pos_w[0, body_idx, :].cpu().numpy()
                positions[body_name] = pos
                print(f"\n{body_name}:")
                print(f"  索引: {body_idx}")
                print(f"  位置: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}]")
            except:
                print(f"\n{body_name}: ⚠️  未找到")
        
        # 计算相对距离
        if "star_link_ee" in positions and "endo360_needle" in positions:
            print("\n" + "=" * 80)
            print("📏 工具长度信息:")
            print("=" * 80)
            
            arm_end = positions["star_link_ee"]
            needle_tip = positions["endo360_needle"]
            
            distance = torch.tensor(needle_tip) - torch.tensor(arm_end)
            length = torch.norm(distance).item()
            
            print(f"\n从机械臂末端到针尖:")
            print(f"  X 偏移: {distance[0]:.4f} m")
            print(f"  Y 偏移: {distance[1]:.4f} m")
            print(f"  Z 偏移: {distance[2]:.4f} m")
            print(f"  总长度: {length:.4f} m ({length*1000:.1f} mm)")
        
        # 显示当前配置
        print("\n" + "=" * 80)
        print("⚙️  当前环境配置:")
        print("=" * 80)
        
        # 从配置中获取末端执行器名称
        from isaaclab_tasks.manager_based.manipulation.reach.config.star.joint_pos_env_cfg import StarReachEnvCfg
        cfg = StarReachEnvCfg()
        cfg.__post_init__()
        
        ee_name = cfg.commands.ee_pose.body_name
        print(f"\n当前末端执行器: {ee_name}")
        
        if ee_name == "endo360_needle":
            print("✅ 配置正确！当前控制工具末端（针尖）")
        elif ee_name == "star_link_ee":
            print("⚠️  当前控制机械臂末端，不包括工具")
        else:
            print(f"ℹ️  当前控制: {ee_name}")
        
        # 工作空间建议
        if "endo360_needle" in positions:
            needle_pos = positions["endo360_needle"]
            print("\n" + "=" * 80)
            print("💡 工作空间建议:")
            print("=" * 80)
            print(f"\n基于当前针尖位置 [{needle_pos[0]:.2f}, {needle_pos[1]:.2f}, {needle_pos[2]:.2f}]")
            print("\n建议的命令范围配置:")
            print("```python")
            print("self.commands.ee_pose.ranges.pos_x = "
                  f"({needle_pos[0]-0.2:.2f}, {needle_pos[0]+0.2:.2f})")
            print("self.commands.ee_pose.ranges.pos_y = "
                  f"({needle_pos[1]-0.2:.2f}, {needle_pos[1]+0.2:.2f})")
            print("self.commands.ee_pose.ranges.pos_z = "
                  f"({max(0.1, needle_pos[2]-0.2):.2f}, {needle_pos[2]+0.2:.2f})")
            print("```")
        
        # 等待用户观察
        print("\n" + "=" * 80)
        print("🎯 可视化检查:")
        print("=" * 80)
        print("\n在 Isaac Sim 窗口中:")
        print("  1. 查看机器人姿态")
        print("  2. 目标点（如果显示）应该在针尖位置")
        print("  3. 按 Ctrl+C 退出")
        print("\n正在等待... (按 Ctrl+C 退出)")
        
        # 简单仿真循环
        for i in range(1000):
            action = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
            obs, reward, terminated, truncated, info = env.step(action)
            
            if i % 100 == 0:
                print(f"  步骤 {i}: 末端执行器位置正常显示中...")
        
        env.close()
        
        print("\n" + "=" * 80)
        print("✅ 验证完成")
        print("=" * 80)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_tool_tip()
    exit(0 if success else 1)

