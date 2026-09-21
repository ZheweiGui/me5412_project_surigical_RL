#!/usr/bin/env python3
# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""检查 star.usd 文件的结构和关节信息

这个脚本会帮助你从 star.usd 文件中提取关键信息，包括：
- 关节名称
- Body/Link 名称
- 初始关节位置

运行: python inspect_star_usd.py
"""

import os
from pxr import Usd, UsdGeom, UsdPhysics

def inspect_usd_file(usd_path: str):
    """检查 USD 文件的结构"""
    
    if not os.path.exists(usd_path):
        print(f"❌ 错误: 找不到文件 {usd_path}")
        print("\n请确保 star.usd 文件在:")
        print("  source/isaaclab_assets/isaaclab_assets/robots/star.usd")
        return False
    
    print("=" * 80)
    print(f"检查 USD 文件: {usd_path}")
    print("=" * 80)
    
    # 打开 USD 文件
    stage = Usd.Stage.Open(usd_path)
    
    if not stage:
        print(f"❌ 错误: 无法打开 USD 文件")
        return False
    
    print("\n✓ USD 文件成功打开")
    
    # 查找所有关节
    joints = []
    bodies = []
    root_prim = None
    
    print("\n" + "=" * 80)
    print("扫描 USD 层级结构...")
    print("=" * 80)
    
    for prim in stage.Traverse():
        # 检查是否是关节
        if prim.IsA(UsdPhysics.Joint) or "joint" in prim.GetName().lower():
            joint_name = prim.GetName()
            joints.append(joint_name)
            print(f"  🔗 关节: {joint_name} (路径: {prim.GetPath()})")
        
        # 检查是否是 rigid body 或 link
        if prim.IsA(UsdGeom.Xformable) and not prim.IsA(UsdPhysics.Joint):
            body_name = prim.GetName()
            # 过滤掉一些常见的非 body 元素
            if any(keyword in body_name.lower() for keyword in ['link', 'body', 'effector', 'gripper', 'ee', 'tool']):
                bodies.append(body_name)
                print(f"  📦 Body/Link: {body_name} (路径: {prim.GetPath()})")
        
        # 查找根 articulation
        if not root_prim and (prim.IsA(UsdPhysics.ArticulationRootAPI) or 
                              any(keyword in prim.GetName().lower() for keyword in ['robot', 'arm', 'base'])):
            root_prim = prim
    
    # 输出总结
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    
    if root_prim:
        print(f"\n✓ 找到根 Prim: {root_prim.GetName()}")
        print(f"  路径: {root_prim.GetPath()}")
    
    print(f"\n✓ 找到 {len(joints)} 个关节:")
    for joint in joints:
        print(f"  - {joint}")
    
    print(f"\n✓ 找到 {len(bodies)} 个 Body/Link:")
    for body in bodies:
        print(f"  - {body}")
    
    # 生成配置建议
    print("\n" + "=" * 80)
    print("配置建议")
    print("=" * 80)
    
    print("\n1️⃣  在 star.py 中，将关节初始位置配置为:")
    print("```python")
    print("init_state=ArticulationCfg.InitialStateCfg(")
    print("    joint_pos={")
    if joints:
        for joint in joints:
            print(f'        "{joint}": 0.0,')
    else:
        print('        ".*": 0.0,  # 匹配所有关节')
    print("    },")
    print("    joint_vel={\".*\": 0.0},")
    print("),")
    print("```")
    
    print("\n2️⃣  在 star.py 中，配置执行器:")
    print("```python")
    print("actuators={")
    if joints:
        # 尝试识别常见模式
        arm_joints = [j for j in joints if any(k in j.lower() for k in ['joint', 'arm'])]
        gripper_joints = [j for j in joints if any(k in j.lower() for k in ['gripper', 'finger'])]
        
        if arm_joints:
            print("    \"star_arm\": ImplicitActuatorCfg(")
            # 尝试生成正则表达式模式
            if len(arm_joints) > 1 and all(c.isdigit() for c in arm_joints[0][-1]):
                # 关节名称以数字结尾
                base_name = ''.join([c for c in arm_joints[0] if not c.isdigit()])
                print(f'        joint_names_expr=["{base_name}[0-9]*"],')
            else:
                print(f'        joint_names_expr={arm_joints},')
            print("        effort_limit_sim=87.0,")
            print("        stiffness=80.0,")
            print("        damping=4.0,")
            print("    ),")
        
        if gripper_joints:
            print("    \"star_gripper\": ImplicitActuatorCfg(")
            print(f'        joint_names_expr={gripper_joints},')
            print("        effort_limit_sim=200.0,")
            print("        stiffness=2e3,")
            print("        damping=1e2,")
            print("    ),")
    else:
        print("    \"star_joints\": ImplicitActuatorCfg(")
        print("        joint_names_expr=[\".*\"],")
        print("        effort_limit_sim=87.0,")
        print("        stiffness=80.0,")
        print("        damping=4.0,")
        print("    ),")
    print("},")
    print("```")
    
    print("\n3️⃣  在 joint_pos_env_cfg.py 中，设置末端执行器:")
    if bodies:
        # 查找可能的末端执行器
        ee_candidates = [b for b in bodies if any(k in b.lower() for k in ['ee', 'effector', 'tool', 'tcp', 'hand'])]
        if ee_candidates:
            print(f'END_EFFECTOR_NAME = "{ee_candidates[0]}"  # 可能的候选: {ee_candidates}')
        else:
            print(f'END_EFFECTOR_NAME = "{bodies[-1]}"  # 通常是最后一个 link')
    else:
        print('END_EFFECTOR_NAME = "end_effector"  # 请检查实际名称')
    
    print("\n4️⃣  在 joint_pos_env_cfg.py 中，配置关节控制:")
    print("```python")
    print("self.actions.arm_action = mdp.JointPositionActionCfg(")
    print("    asset_name=\"robot\",")
    if joints:
        arm_joints = [j for j in joints if 'gripper' not in j.lower() and 'finger' not in j.lower()]
        if arm_joints:
            print(f"    joint_names={arm_joints},")
        else:
            print("    joint_names=[\".*\"],")
    else:
        print("    joint_names=[\".*\"],")
    print("    scale=0.5,")
    print("    use_default_offset=True")
    print(")")
    print("```")
    
    print("\n" + "=" * 80)
    print("后续步骤")
    print("=" * 80)
    print("\n1. 根据上述建议更新配置文件:")
    print("   - source/isaaclab_assets/isaaclab_assets/robots/star.py")
    print("   - source/isaaclab_tasks/.../reach/config/star/joint_pos_env_cfg.py")
    print("\n2. 运行测试脚本:")
    print("   python test_star_env.py")
    print("\n3. 如果测试通过，开始训练:")
    print("   ./train_star_reach.sh")
    
    return True


if __name__ == "__main__":
    # USD 文件路径
    usd_path = "source/isaaclab_assets/isaaclab_assets/robots/star.usd"
    
    try:
        success = inspect_usd_file(usd_path)
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        print("\n请确保:")
        print("1. star.usd 文件存在于指定路径")
        print("2. 已安装 pxr (USD) Python 包")
        exit(1)

