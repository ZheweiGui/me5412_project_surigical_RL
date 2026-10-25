# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Configuration for the STAR robot."""

import os

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

##
# Configuration
##

STAR_USD_PATH = os.path.join(os.path.dirname(__file__), "star.usd")

STAR_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=STAR_USD_PATH,
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=12,
            solver_velocity_iteration_count=1,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "star_joint_[1-7]": 0.0,
            "endo360_joint_1": 0.0,
        },
        joint_vel={".*": 0.0},
    ),
    actuators={
        "star_arm": ImplicitActuatorCfg(
            joint_names_expr=["star_joint_[1-7]"],
            effort_limit_sim=100,
            stiffness=200,
            damping=50.0,
        ),
        "endo360_tool": ImplicitActuatorCfg(
            joint_names_expr=["endo360_joint_1"],
            effort_limit_sim=100,
            stiffness=200,
            damping=50.0,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
