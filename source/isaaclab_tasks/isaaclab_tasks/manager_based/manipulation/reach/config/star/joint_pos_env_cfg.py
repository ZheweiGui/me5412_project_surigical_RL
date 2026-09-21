# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

from isaaclab.utils import configclass

import isaaclab_tasks.manager_based.manipulation.reach.mdp as mdp
from isaaclab_tasks.manager_based.manipulation.reach.reach_env_cfg import ReachEnvCfg

##
# Pre-defined configs
##
from isaaclab_assets import STAR_CFG  # isort: skip


##
# Environment configuration
##


@configclass
class StarReachEnvCfg(ReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        self.decimation = 4  # 从2改为4
        self.sim.dt = 1.0 / 240.0  # 从60Hz改为240Hz，接近400Hz

        # switch robot to star
        self.scene.robot = STAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        
        # 末端执行器名称 - 使用工具的实际末端而不是机械臂末端
        # star_link_ee: 机械臂本身的末端
        # endo360_needle: 工具（针）的末端 - 用于实际控制
        END_EFFECTOR_NAME = "endo360_needle"  # 工具末端（针尖）
        
        # override rewards - 使用你的末端执行器名称
        self.rewards.end_effector_position_tracking.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]
        self.rewards.end_effector_position_tracking_fine_grained.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]
        self.rewards.end_effector_orientation_tracking.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]

        # override actions - 控制机械臂关节和工具关节
        # 注意：这里控制所有8个主动关节（7个机械臂 + 1个工具）
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot", 
            joint_names=["star_joint_[1-7]", "endo360_joint_1"],  # 精确匹配所有8个主动关节
            scale=0.5, 
            use_default_offset=True
        )
        
        # override command generator body
        self.commands.ee_pose.body_name = END_EFFECTOR_NAME
        # 设置末端执行器的方向约束（假设沿 z 方向，如有需要可调整）
        self.commands.ee_pose.ranges.pitch = (math.pi, math.pi)
        
        # Add success termination for tracking success rate
        # Success criteria: position error < 1cm AND orientation error < 10 degrees
        from isaaclab.managers import TerminationTermCfg as DoneTerm
        from isaaclab.managers import SceneEntityCfg
        self.terminations.success = DoneTerm(
            func=mdp.is_success,
            params={
                "command_name": "ee_pose",
                "asset_cfg": SceneEntityCfg("robot", body_names=[END_EFFECTOR_NAME]),
                "position_threshold": 0.1,  # 1cm
                "orientation_threshold": 0.349,  # 10 degrees in radians
            },
        )


@configclass
class StarReachEnvCfg_PLAY(StarReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False
        
        # 固定 episode 长度为 200 步
        # 计算: 200 control steps * step_dt (decimation * sim.dt)
        # step_dt = 4 * (1/240) = 1/60 秒
        # 所以 200 步 = 200/60 = 3.33 秒
        self.step_dt = 1 / 60
        max_episode_steps = 200
        self.episode_length_s = max_episode_steps * self.step_dt
        
        # Play 模式：只保留 time_out termination
        # 父类添加了 success termination，我们需要移除它
        # 这样环境只会在固定 200 步后统一 reset，不受其他条件影响
        
        # 删除父类添加的 success termination
        if hasattr(self.terminations, 'success'):
            # 直接删除这个属性
            object.__delattr__(self.terminations, 'success')
        
        # 确保 reset 时机械臂回到初始位置
        # 父类已经有 reset_robot_joints 事件，这里明确设置为回到默认位置（不随机）
        from isaaclab.managers import EventTermCfg as EventTerm
        self.events.reset_robot_joints = EventTerm(
            func=mdp.reset_joints_by_offset,
            mode="reset",
            params={
                "position_range": (0.0, 0.0),  # 不随机，回到初始位置
                "velocity_range": (0.0, 0.0),  # 速度为0
            },
        )

