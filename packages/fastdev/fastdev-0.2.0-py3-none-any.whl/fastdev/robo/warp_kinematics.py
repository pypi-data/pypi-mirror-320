# mypy: disable-error-code="valid-type"
from typing import TYPE_CHECKING, Optional, Tuple

import numpy as np
import torch
import warp as wp
from jaxtyping import Float

if TYPE_CHECKING:
    from fastdev.robo.articulation import Articulation


@wp.func
def axis_angle_to_tf_mat(axis: wp.vec3, angle: wp.float32):
    x, y, z = axis[0], axis[1], axis[2]
    s, c = wp.sin(angle), wp.cos(angle)
    C = 1.0 - c

    xs, ys, zs = x * s, y * s, z * s
    xC, yC, zC = x * C, y * C, z * C
    xyC, yzC, zxC = x * yC, y * zC, z * xC

    # fmt: off
    return wp.mat44(
        x * xC + c, xyC - zs, zxC + ys, 0.0,
        xyC + zs, y * yC + c, yzC - xs, 0.0,
        zxC - ys, yzC + xs, z * zC + c, 0.0,
        0.0, 0.0, 0.0, 1.0,
    )
    # fmt: on


@wp.func
def axis_distance_to_tf_mat(axis: wp.vec3, distance: wp.float32):
    x, y, z = axis[0], axis[1], axis[2]
    # fmt: off
    return wp.mat44(
        1.0, 0.0, 0.0, distance * x,
        0.0, 1.0, 0.0, distance * y,
        0.0, 0.0, 1.0, distance * z,
        0.0, 0.0, 0.0, 1.0,
    )
    # fmt: on


@wp.kernel
def forward_kinematics_kernel(
    joint_values: wp.array2d(dtype=wp.float32),  # [b, num_dofs]
    root_poses: wp.array2d(dtype=wp.mat44),  # [b, num_arti, 4, 4], optional
    joint_first_indices: wp.array(dtype=wp.int32),
    link_indices_topological_order: wp.array(dtype=wp.int32),
    parent_link_indices: wp.array(dtype=wp.int32),
    link_joint_indices: wp.array(dtype=wp.int32),
    link_joint_types: wp.array(dtype=wp.int32),
    link_joint_origins: wp.array(dtype=wp.mat44),
    link_joint_axes: wp.array(dtype=wp.vec3),
    link_first_indices: wp.array(dtype=wp.int32),
    link_poses: wp.array2d(dtype=wp.mat44),  # output, [b, num_links]
):
    b_idx, arti_idx = wp.tid()
    joint_first_idx = joint_first_indices[arti_idx]
    link_first_idx = link_first_indices[arti_idx]
    if arti_idx == wp.int32(link_first_indices.shape[0] - 1):
        link_last_idx = wp.int32(link_indices_topological_order.shape[0])
    else:
        link_last_idx = link_first_indices[arti_idx + 1]

    if root_poses.shape[0] > 0:
        root_pose = root_poses[b_idx, arti_idx]
    else:
        root_pose = wp.identity(n=4, dtype=wp.float32)  # type: ignore

    for glb_topo_idx in range(link_first_idx, link_last_idx):
        glb_link_idx = link_indices_topological_order[glb_topo_idx] + link_first_idx
        joint_type = link_joint_types[glb_link_idx]
        if joint_type == -1:  # Root link
            glb_joint_pose = root_pose
        else:  # Non-root links
            glb_parent_link_idx = parent_link_indices[glb_link_idx] + link_first_idx
            parent_link_pose = link_poses[b_idx, glb_parent_link_idx]
            glb_joint_idx = link_joint_indices[glb_link_idx] + joint_first_idx
            if joint_type == 0:
                local_joint_tf = wp.identity(n=4, dtype=wp.float32)  # type: ignore
            elif joint_type == 1:  # prismatic
                joint_value = joint_values[b_idx, glb_joint_idx]
                joint_axis = link_joint_axes[glb_link_idx]
                local_joint_tf = axis_distance_to_tf_mat(joint_axis, joint_value)
            elif joint_type == 2:  # revolute
                joint_value = joint_values[b_idx, glb_joint_idx]
                joint_axis = link_joint_axes[glb_link_idx]
                local_joint_tf = axis_angle_to_tf_mat(joint_axis, joint_value)
            joint_origin = link_joint_origins[glb_link_idx]
            glb_joint_pose = (parent_link_pose @ joint_origin) @ local_joint_tf  # type: ignore
        link_poses[b_idx, glb_link_idx] = glb_joint_pose


_KERNEL_PARAMS_TYPES_AND_GETTERS = {
    "joint_first_indices": (wp.int32, "get_joint_first_indices"),
    "link_indices_topological_order": (wp.int32, "get_packed_link_indices_topological_order"),
    "parent_link_indices": (wp.int32, "get_packed_parent_link_indices"),
    "link_joint_indices": (wp.int32, "get_packed_link_joint_indices"),
    "link_joint_types": (wp.int32, "get_packed_link_joint_types"),
    "link_joint_origins": (wp.mat44, "get_packed_link_joint_origins"),
    "link_joint_axes": (wp.vec3, "get_packed_link_joint_axes"),
    "link_first_indices": (wp.int32, "get_link_first_indices"),
}


class ForwardKinematics(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        joint_values: Float[torch.Tensor, "... total_num_joints"],
        articulation: "Articulation",
        root_poses: Optional[Float[torch.Tensor, "... num_arti 4 4"]] = None,
    ) -> Float[torch.Tensor, "... total_num_links 4 4"]:
        batch_shape = joint_values.shape[:-1]
        total_num_joints = joint_values.shape[-1]
        total_num_links = articulation.total_num_links
        num_arti = articulation.num_arti
        requires_grad = joint_values.requires_grad or (root_poses is not None and root_poses.requires_grad)

        joint_values_wp = wp.from_torch(
            joint_values.contiguous().view(-1, total_num_joints),
            dtype=wp.float32,
            requires_grad=joint_values.requires_grad,
        )
        root_poses_wp = (
            wp.from_torch(
                root_poses.contiguous().view(-1, num_arti, 4, 4),
                dtype=wp.mat44,
                requires_grad=root_poses.requires_grad,
            )
            if root_poses is not None
            else wp.zeros(shape=(0, 0), dtype=wp.mat44, requires_grad=False, device=joint_values_wp.device)
        )
        link_poses_wp = wp.from_torch(
            torch.zeros(
                (joint_values_wp.shape[0], total_num_links, 4, 4),
                device=joint_values.device,
                dtype=joint_values.dtype,
                requires_grad=requires_grad,
            ),
            dtype=wp.mat44,
            requires_grad=requires_grad,
        )
        wp_params = {
            name: wp.from_torch(getattr(articulation, fn)(return_tensors="pt"), dtype=dtype)
            for name, (dtype, fn) in _KERNEL_PARAMS_TYPES_AND_GETTERS.items()
        }

        wp.launch(
            kernel=forward_kinematics_kernel,
            dim=(joint_values_wp.shape[0], num_arti),
            inputs=[joint_values_wp, root_poses_wp, *wp_params.values()],
            outputs=[link_poses_wp],
            device=joint_values_wp.device,
        )

        if joint_values_wp.requires_grad or root_poses_wp.requires_grad:
            ctx.shapes = (batch_shape, total_num_joints, total_num_links, num_arti)
            ctx.joint_values_wp = joint_values_wp
            ctx.root_poses_wp = root_poses_wp
            ctx.link_poses_wp = link_poses_wp
            ctx.wp_params = wp_params

        return wp.to_torch(link_poses_wp).view(*batch_shape, total_num_links, 4, 4)

    @staticmethod
    def backward(  # type: ignore
        ctx, link_poses_grad: Float[torch.Tensor, "... total_num_links 4 4"]
    ) -> Tuple[
        Optional[Float[torch.Tensor, "... total_num_joints"]],
        None,
        Optional[Float[torch.Tensor, "... num_arti 4 4"]],
    ]:
        if not ctx.joint_values_wp.requires_grad and (not ctx.root_poses_wp.requires_grad):
            return None, None, None

        batch_shape, total_num_joints, total_num_links, num_arti = ctx.shapes
        ctx.link_poses_wp.grad = wp.from_torch(
            link_poses_grad.contiguous().view(-1, total_num_links, 4, 4), dtype=wp.mat44
        )

        wp.launch(
            kernel=forward_kinematics_kernel,
            dim=(ctx.joint_values_wp.shape[0], num_arti),
            inputs=[ctx.joint_values_wp, ctx.root_poses_wp, *ctx.wp_params.values()],
            outputs=[ctx.link_poses_wp],
            adj_inputs=[ctx.joint_values_wp.grad, ctx.root_poses_wp.grad, *([None] * len(ctx.wp_params))],
            adj_outputs=[ctx.link_poses_wp.grad],
            adjoint=True,
            device=ctx.joint_values_wp.device,
        )

        joint_values_grad = (
            wp.to_torch(ctx.joint_values_wp.grad).view(*batch_shape, total_num_joints)
            if ctx.joint_values_wp.requires_grad
            else None
        )
        root_poses_grad = (
            wp.to_torch(ctx.root_poses_wp.grad).view(*batch_shape, num_arti, 4, 4)
            if ctx.root_poses_wp.requires_grad
            else None
        )
        return joint_values_grad, None, root_poses_grad


def forward_kinematics(
    joint_values: Float[torch.Tensor, "... total_num_joints"],
    articulation: "Articulation",
    root_poses: Optional[Float[torch.Tensor, "... num_arti 4 4"]] = None,
) -> Float[torch.Tensor, "... total_num_links 4 4"]:
    return ForwardKinematics.apply(joint_values, articulation, root_poses)


def forward_kinematics_numpy(
    joint_values: Float[np.ndarray, "... total_num_joints"],  # noqa: F821
    articulation: "Articulation",
    root_poses: Optional[Float[np.ndarray, "... num_arti 4 4"]] = None,
) -> Float[np.ndarray, "... total_num_links 4 4"]:
    total_num_joints = joint_values.shape[-1]
    total_num_links = articulation.total_num_links
    num_arti = articulation.num_arti
    joint_values_wp = wp.from_numpy(joint_values.reshape(-1, total_num_joints), dtype=wp.float32)  # [B, num_dofs]
    link_poses_wp = wp.from_numpy(
        np.zeros(
            (joint_values_wp.shape[0], total_num_links, 4, 4),
            dtype=joint_values.dtype,
        ),
        dtype=wp.mat44,
    )
    root_poses_wp = (
        wp.from_numpy(root_poses.reshape(-1, num_arti, 4, 4), dtype=wp.mat44)
        if root_poses is not None
        else wp.zeros(shape=(0, 0), dtype=wp.mat44, requires_grad=False, device=joint_values_wp.device)
    )
    wp_params = {
        name: wp.from_numpy(getattr(articulation, fn)("np"), dtype=dtype)
        for name, (dtype, fn) in _KERNEL_PARAMS_TYPES_AND_GETTERS.items()
    }
    wp.launch(
        kernel=forward_kinematics_kernel,
        dim=(joint_values_wp.shape[0], num_arti),
        inputs=[joint_values_wp, root_poses_wp, *wp_params.values()],
        outputs=[link_poses_wp],
        device=joint_values_wp.device,
    )
    return link_poses_wp.numpy().reshape(joint_values.shape[:-1] + (total_num_links, 4, 4))
