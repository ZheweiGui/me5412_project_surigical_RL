# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass

import isaaclab_tasks.manager_based.manipulation.reach.mdp as mdp
from isaaclab_tasks.manager_based.manipulation.reach.reach_env_cfg import ReachEnvCfg

##
# Pre-defined configs
##
from isaaclab_assets import STAR_CFG  # isort: skip

END_EFFECTOR_NAME = "endo360_needle"
POSITION_SUCCESS_THRESHOLD = 0.01
ORIENTATION_SUCCESS_THRESHOLD = math.radians(10.0)


##
# Environment configuration
##


@configclass
class StarReachEnvCfg(ReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        self.decimation = 4
        self.sim.dt = 1.0 / 240.0
        self.sim.render_interval = self.decimation

        # switch robot to star
        self.scene.robot = STAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

        # Track the mounted tool tip rather than the bare arm flange.
        self.rewards.end_effector_position_tracking.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]
        self.rewards.end_effector_position_tracking_fine_grained.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]
        self.rewards.end_effector_orientation_tracking.params["asset_cfg"].body_names = [END_EFFECTOR_NAME]

        # Control all seven arm joints and the Endo360 tool joint.
        self.actions.arm_action = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=["star_joint_[1-7]", "endo360_joint_1"],
            scale=0.5,
            use_default_offset=True,
        )

        # override command generator body
        self.commands.ee_pose.body_name = END_EFFECTOR_NAME
        self.commands.ee_pose.ranges.pitch = (math.pi, math.pi)

        self.terminations.success = DoneTerm(
            func=mdp.is_success,
            params={
                "command_name": "ee_pose",
                "asset_cfg": SceneEntityCfg("robot", body_names=[END_EFFECTOR_NAME]),
                "position_threshold": POSITION_SUCCESS_THRESHOLD,
                "orientation_threshold": ORIENTATION_SUCCESS_THRESHOLD,
            },
        )


@configclass
class StarReachEnvCfg_PLAY(StarReachEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # Keep playback light and deterministic.
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False

        # Use fixed-length episodes so all playback environments reset together.
        self.episode_length_s = 200 * self.decimation * self.sim.dt
        self.terminations.success = None

        self.events.reset_robot_joints = EventTerm(
            func=mdp.reset_joints_by_offset,
            mode="reset",
            params={
                "position_range": (0.0, 0.0),
                "velocity_range": (0.0, 0.0),
            },
        )
