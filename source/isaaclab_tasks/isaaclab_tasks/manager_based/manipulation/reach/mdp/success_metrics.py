# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Success metrics for reach task."""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import RigidObject
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude, quat_mul

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def is_success(
    env: ManagerBasedRLEnv,
    command_name: str,
    asset_cfg: SceneEntityCfg,
    position_threshold: float = 0.01,  # 1cm
    orientation_threshold: float = 0.1745,  # 10 degrees in radians
) -> torch.Tensor:
    """Check if the task is successful.
    
    Success criteria:
    - Position error < position_threshold (default: 1cm)
    - Orientation error < orientation_threshold (default: 10 degrees)
    
    Args:
        env: The environment.
        command_name: Name of the command.
        asset_cfg: Asset configuration.
        position_threshold: Maximum position error in meters (default: 0.01m = 1cm).
        orientation_threshold: Maximum orientation error in radians (default: 0.1745 rad = 10 deg).
    
    Returns:
        Boolean tensor indicating success for each environment.
    """
    # Extract the asset
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    
    # Check position error
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(asset.data.root_pos_w, asset.data.root_quat_w, des_pos_b)
    curr_pos_w = asset.data.body_pos_w[:, asset_cfg.body_ids[0]]
    position_error = torch.norm(curr_pos_w - des_pos_w, dim=1)
    
    # Check orientation error
    des_quat_b = command[:, 3:7]
    des_quat_w = quat_mul(asset.data.root_quat_w, des_quat_b)
    curr_quat_w = asset.data.body_quat_w[:, asset_cfg.body_ids[0]]
    orientation_error = quat_error_magnitude(curr_quat_w, des_quat_w)
    
    # Success if both errors are below thresholds
    position_success = position_error < position_threshold
    orientation_success = orientation_error < orientation_threshold
    success = position_success & orientation_success
    
    return success  # Return as boolean tensor


def position_error_cm(
    env: ManagerBasedRLEnv,
    command_name: str,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Get position error in centimeters for logging.
    
    Args:
        env: The environment.
        command_name: Name of the command.
        asset_cfg: Asset configuration.
    
    Returns:
        Position error in centimeters.
    """
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    
    des_pos_b = command[:, :3]
    des_pos_w, _ = combine_frame_transforms(asset.data.root_pos_w, asset.data.root_quat_w, des_pos_b)
    curr_pos_w = asset.data.body_pos_w[:, asset_cfg.body_ids[0]]
    position_error_m = torch.norm(curr_pos_w - des_pos_w, dim=1)
    
    return position_error_m * 100.0  # Convert to cm


def orientation_error_deg(
    env: ManagerBasedRLEnv,
    command_name: str,
    asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Get orientation error in degrees for logging.
    
    Args:
        env: The environment.
        command_name: Name of the command.
        asset_cfg: Asset configuration.
    
    Returns:
        Orientation error in degrees.
    """
    asset: RigidObject = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    
    des_quat_b = command[:, 3:7]
    des_quat_w = quat_mul(asset.data.root_quat_w, des_quat_b)
    curr_quat_w = asset.data.body_quat_w[:, asset_cfg.body_ids[0]]
    orientation_error_rad = quat_error_magnitude(curr_quat_w, des_quat_w)
    
    return torch.rad2deg(orientation_error_rad)  # Convert to degrees

