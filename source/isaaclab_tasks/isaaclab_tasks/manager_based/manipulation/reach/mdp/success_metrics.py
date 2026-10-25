# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Success metrics for reach task."""

from __future__ import annotations

import torch
from typing import TYPE_CHECKING

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import combine_frame_transforms, quat_error_magnitude, quat_mul

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def _pose_errors(
    env: ManagerBasedRLEnv, command_name: str, asset_cfg: SceneEntityCfg
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return position and orientation errors in meters and radians."""
    asset: Articulation = env.scene[asset_cfg.name]
    command = env.command_manager.get_command(command_name)
    body_id = asset_cfg.body_ids[0]

    desired_position_body = command[:, :3]
    desired_position_world, _ = combine_frame_transforms(
        asset.data.root_pos_w, asset.data.root_quat_w, desired_position_body
    )
    current_position_world = asset.data.body_pos_w[:, body_id]
    position_error = torch.linalg.vector_norm(current_position_world - desired_position_world, dim=1)

    desired_orientation_body = command[:, 3:7]
    desired_orientation_world = quat_mul(asset.data.root_quat_w, desired_orientation_body)
    current_orientation_world = asset.data.body_quat_w[:, body_id]
    orientation_error = quat_error_magnitude(current_orientation_world, desired_orientation_world)

    return position_error, orientation_error


def is_success(
    env: ManagerBasedRLEnv,
    command_name: str,
    asset_cfg: SceneEntityCfg,
    position_threshold: float = 0.01,
    orientation_threshold: float = 0.1745,
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
    position_error, orientation_error = _pose_errors(env, command_name, asset_cfg)
    return (position_error < position_threshold) & (orientation_error < orientation_threshold)


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
    position_error_m, _ = _pose_errors(env, command_name, asset_cfg)
    return position_error_m * 100.0


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
    _, orientation_error_rad = _pose_errors(env, command_name, asset_cfg)
    return torch.rad2deg(orientation_error_rad)
