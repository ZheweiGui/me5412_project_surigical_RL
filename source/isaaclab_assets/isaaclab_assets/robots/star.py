# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the Star robot.

This is a custom robot configuration for the Star robot.
"""

import os
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

##
# Configuration
##

# Get the path to the star.usd file
STAR_USD_PATH = os.path.join(os.path.dirname(__file__), "star.usd")

STAR_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=STAR_USD_PATH,
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True,  # 禁用重力，减少对关节的负担
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True, 
            solver_position_iteration_count=12,  # 增加求解器迭代次数以提高稳定性
            solver_velocity_iteration_count=1    # 启用速度迭代
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            # Star 机械臂关节初始位置 (star_joint_1 到 star_joint_7)
            "star_joint_[1-7]": 0.0,
            # Endo360 工具关节初始位置 (endo360_joint_1)
            "endo360_joint_1": 0.0,
        },
        joint_vel={".*": 0.0},
    ),
    actuators={
        # Star 机械臂关节执行器 (star_joint_1 到 star_joint_7) - 7个关节
        "star_arm": ImplicitActuatorCfg(
            joint_names_expr=["star_joint_[1-7]"],  # 精确匹配 star_joint_1 到 star_joint_7
            effort_limit_sim=100,
            stiffness=200,  # 高刚度减少抖动
            damping=50.0,     # 高阻尼减少震荡
        ),
        # Endo360 工具关节执行器 (endo360_joint_1) - 1个关节
        "endo360_tool": ImplicitActuatorCfg(
            joint_names_expr=["endo360_joint_1"],  # 工具关节
            effort_limit_sim=100,
            stiffness=200,  # 工具需要更高刚度保持稳定
            damping=50.0,     # 更高阻尼
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
"""Configuration of Star robot.

注意：这是一个模板配置，需要根据你的 star.usd 文件中的实际关节名称和参数进行调整：
1. joint_pos: 设置初始关节位置（使用实际的关节名称）
2. actuators: 配置执行器参数（关节名称表达式、力矩限制、刚度、阻尼等）
3. 如果机器人有抓手，需要单独配置抓手执行器

你可以使用 Isaac Sim 打开 star.usd 文件来查看关节名称和层级结构。
"""

