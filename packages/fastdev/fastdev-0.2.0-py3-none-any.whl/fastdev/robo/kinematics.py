from typing import TYPE_CHECKING, Optional

import torch
from jaxtyping import Float

from fastdev.xform.rotation import axis_angle_to_matrix  # warp's version may don't support broadcasting, use this
from fastdev.xform.transforms import rot_tl_to_tf_mat

if TYPE_CHECKING:
    from fastdev.robo.articulation import Articulation


def forward_kinematics(
    joint_values: Float[torch.Tensor, "... total_num_joints"],
    articulation: "Articulation",
    root_poses: Optional[Float[torch.Tensor, "... num_arti 4 4"]] = None,
) -> Float[torch.Tensor, "... total_num_links 4 4"]:
    """
    NOTE After adding multi-articulation support, this implementation has slower backward pass performance compared to `pytorch-kinematics`.
    """
    batch_shape = joint_values.shape[:-1]
    total_num_links = articulation.total_num_links
    device = joint_values.device
    requires_grad = joint_values.requires_grad or (root_poses is not None and root_poses.requires_grad)

    link_poses = torch.eye(4, device=device, requires_grad=requires_grad).repeat(*batch_shape, total_num_links, 1, 1)

    if root_poses is None:
        root_poses = torch.eye(4, device=device).expand(*batch_shape, articulation.num_arti, 4, 4)

    joint_axes = articulation.get_packed_full_joint_axes(return_tensors="pt")
    pris_jnt_tf = rot_tl_to_tf_mat(tl=joint_axes * joint_values.unsqueeze(-1))  # type: ignore
    rev_jnt_tf = rot_tl_to_tf_mat(rot_mat=axis_angle_to_matrix(joint_axes, joint_values))  # type: ignore

    link_topo_indices = articulation.get_packed_link_indices_topological_order(return_tensors="pt")
    parent_link_indices = articulation.get_packed_parent_link_indices(return_tensors="pt")
    link_joint_types = articulation.get_packed_link_joint_types(return_tensors="pt")
    link_joint_indices = articulation.get_packed_link_joint_indices(return_tensors="pt")
    link_joint_origins = articulation.get_packed_link_joint_origins(return_tensors="pt")
    joint_first_indices = articulation.get_joint_first_indices(return_tensors="pt")
    link_first_indices = articulation.get_link_first_indices(return_tensors="pt")

    identity_matrix = torch.eye(4, device=device).expand(*batch_shape, 4, 4)
    for arti_idx in range(articulation.num_arti):
        link_start = link_first_indices[arti_idx].item()
        link_end = (
            link_first_indices[arti_idx + 1].item()
            if arti_idx < len(link_first_indices) - 1
            else len(link_topo_indices)
        )
        joint_start = joint_first_indices[arti_idx].item()

        for local_link_idx in link_topo_indices[link_start:link_end]:  # type: ignore
            glb_link_idx = local_link_idx + link_start
            joint_type = link_joint_types[glb_link_idx]
            if joint_type == -1:  # Root link
                link_poses[..., glb_link_idx, :, :] = root_poses[..., arti_idx, :, :]
                continue
            glb_parent_idx = parent_link_indices[glb_link_idx] + link_start
            parent_pose = link_poses[..., glb_parent_idx, :, :]
            if joint_type == 1:  # Prismatic
                glb_joint_idx = link_joint_indices[glb_link_idx] + joint_start
                local_tf = pris_jnt_tf[..., glb_joint_idx, :, :]
            elif joint_type == 2:  # Revolute
                glb_joint_idx = link_joint_indices[glb_link_idx] + joint_start
                local_tf = rev_jnt_tf[..., glb_joint_idx, :, :]
            else:  # Fixed
                local_tf = identity_matrix
            origin = link_joint_origins[glb_link_idx]
            link_poses[..., glb_link_idx, :, :] = (parent_pose @ origin) @ local_tf
    return link_poses
