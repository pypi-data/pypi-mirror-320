import random

import numpy as np
import torch
from fastdev.robo.articulation import Articulation, ArticulationSpec


def test_basic():
    device = "cpu"
    arti = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/panda.urdf"), device=device)
    assert arti.total_num_dofs == 8
    joint_values = torch.tensor([[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = arti.forward_kinematics(joint_values)
    expected_link_pose = torch.tensor(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
    link_poses[:, -2, :3, 3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor([[0.2193, 0.1663, 0.1481, -0.0204, 0.0791, 0.2665, -0.0185, -0.1392]], device=device)
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)

    # test batch size
    link_poses = arti.forward_kinematics(joint_values[0])
    assert torch.allclose(link_poses[-1], expected_link_pose, atol=1e-4)

    # test joint_names arg
    joint_reindex = list(range(arti.first_spec.num_dofs))
    random.shuffle(joint_reindex)
    link_poses = arti.forward_kinematics(
        joint_values[:, joint_reindex], joint_names=[arti.first_spec.active_joint_names[i] for i in joint_reindex]
    )
    assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
    # test batch size
    link_poses = arti.forward_kinematics(
        joint_values[0, joint_reindex], joint_names=[arti.first_spec.active_joint_names[i] for i in joint_reindex]
    )
    assert torch.allclose(link_poses[-1], expected_link_pose, atol=1e-4)

    # test root_poses arg
    root_poses = torch.eye(4).to(joint_values).unsqueeze(0)
    root_poses[0, 0, 3] = 0.1
    link_poses = arti.forward_kinematics(joint_values, root_poses=root_poses)
    expected_link_pose[0, 3] += 0.1
    assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)

    # test batch size
    link_poses = arti.forward_kinematics(joint_values[None], root_poses=root_poses)
    assert torch.allclose(link_poses[0, 0, -1], expected_link_pose, atol=1e-4)

    if torch.cuda.is_available():
        device = "cuda"
        arti = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/panda.urdf"), device=device)
        joint_values = torch.tensor([[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02]], dtype=torch.float32, device=device)
        joint_values.requires_grad_(True)
        link_poses = arti.forward_kinematics(joint_values)
        expected_link_pose = torch.tensor(
            [
                [0.4639, 0.7548, -0.4637, 0.2874],
                [0.8131, -0.5706, -0.1155, 0.1212],
                [-0.3518, -0.3235, -0.8784, 0.7954],
                [0.0000, 0.0000, 0.0000, 1.0000],
            ],
            device=device,
        )
        assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
        link_poses[:, -2, :3, 3].abs().sum().backward()
        joint_values_grad = joint_values.grad.clone()  # type: ignore
        expected_grad = torch.tensor(
            [[0.2193, 0.1663, 0.1481, -0.0204, 0.0791, 0.2665, -0.0185, -0.1392]], device=device
        )
        assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    arti = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/kuka_iiwa.urdf"), device=device)
    joint_values = torch.tensor([[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = arti.forward_kinematics(joint_values)
    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)
    link_poses[:, -1, :3, :3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor([[0.4059, 1.4686, 0.3498, -1.4969, 0.3350, 1.4344, 0.4556]], device=device)
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)


def test_mjcf():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    robot_model = Articulation(
        ArticulationSpec(
            urdf_or_mjcf_path="assets/robot_description/kuka_iiwa14.xml",
            mjcf_assets={
                "link_0.obj": "",
                "link_1.obj": "",
                "link_2_orange.obj": "",
                "link_2_grey.obj": "",
                "link_3.obj": "",
                "band.obj": "",
                "kuka.obj": "",
                "link_4_orange.obj": "",
                "link_4_grey.obj": "",
                "link_5.obj": "",
                "link_6_orange.obj": "",
                "link_6_grey.obj": "",
                "link_7.obj": "",
            },
        ),
        device=device,
    )
    joint_values = torch.tensor([[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = robot_model.forward_kinematics(joint_values)
    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)

    link_poses[:, -1, :3, :3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor([[0.4059, 1.4686, 0.3498, -1.4969, 0.3350, 1.4344, 0.4556]], device=device)
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)

    # test batch size
    link_poses = robot_model.forward_kinematics(joint_values[0])
    assert torch.allclose(link_poses[-3], expected_link_pose, atol=1e-4)
    link_poses = robot_model.forward_kinematics(joint_values[None])
    assert torch.allclose(link_poses[0, 0, -3], expected_link_pose, atol=1e-4)


def test_multi_chain():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    robot_model = Articulation(
        ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/shadow_hand_right.urdf"),
        device=device,
    )
    joint_values = torch.tensor([[0.15] * 24], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)

    expected_link_pose = torch.tensor(
        [
            [-0.1538, -0.7761, 0.6115, 0.0726],
            [0.9513, 0.0511, 0.3041, 0.0148],
            [-0.2672, 0.6285, 0.7305, 0.4143],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    link_poses = robot_model.forward_kinematics(joint_values)
    assert torch.allclose(
        link_poses[0, robot_model.first_spec.link_names.index("lftip")], expected_link_pose, atol=1e-4
    )

    link_poses[:, :, :3, :3].abs().sum().backward()
    grad = joint_values.grad.clone()  # type: ignore
    # fmt: off
    expected_grad = torch.tensor(
        [[25.4212, 34.2540, -0.8519,  3.3568,  2.0163,  1.0683, -0.8519,  3.3568, 2.0163,  1.0683,  7.9247,  3.8035,
        2.2961, 1.2243,  6.8456,  7.5744, 2.8183,  2.0165,  1.0392,  3.0932,  7.3272,  5.6045, -0.1056, -0.3911]],
        device=device,
    )
    # fmt: on
    assert torch.allclose(grad, expected_grad, atol=1e-3)

    # test batch size
    link_poses = robot_model.forward_kinematics(joint_values[0])
    assert torch.allclose(link_poses[robot_model.first_spec.link_names.index("lftip")], expected_link_pose, atol=1e-4)
    link_poses = robot_model.forward_kinematics(joint_values[None])
    assert torch.allclose(
        link_poses[0, 0, robot_model.first_spec.link_names.index("lftip")], expected_link_pose, atol=1e-4
    )


def test_numpy():
    robot_model = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/panda.urdf"))
    assert robot_model.total_num_dofs == 8
    joint_values = np.array([[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02]])
    link_poses = robot_model.forward_kinematics_numpy(joint_values)
    expected_link_pose = np.array(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert np.allclose(link_poses[0, -1], expected_link_pose, atol=1e-3)

    # test joint_names arg
    joint_reindex = list(range(robot_model.total_num_dofs))
    random.shuffle(joint_reindex)
    link_poses = robot_model.forward_kinematics_numpy(
        joint_values[:, joint_reindex],
        joint_names=[robot_model.first_spec.active_joint_names[i] for i in joint_reindex],
    )
    assert np.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)

    # test root_poses arg
    root_poses = np.eye(4)[None]
    root_poses[0, 0, 3] = 0.1
    link_poses = robot_model.forward_kinematics_numpy(joint_values, root_poses=root_poses)
    expected_link_pose[0, 3] += 0.1
    assert np.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)

    robot_model = Articulation(
        ArticulationSpec(
            urdf_or_mjcf_path="assets/robot_description/kuka_iiwa14.xml",
            mjcf_assets={
                "link_0.obj": "",
                "link_1.obj": "",
                "link_2_orange.obj": "",
                "link_2_grey.obj": "",
                "link_3.obj": "",
                "band.obj": "",
                "kuka.obj": "",
                "link_4_orange.obj": "",
                "link_4_grey.obj": "",
                "link_5.obj": "",
                "link_6_orange.obj": "",
                "link_6_grey.obj": "",
                "link_7.obj": "",
            },
        )
    )
    joint_values = np.array([[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1]], dtype=np.float32)
    link_poses = robot_model.forward_kinematics_numpy(joint_values)

    expected_link_pose = np.array(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert np.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)

    robot_model = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/shadow_hand_right.urdf"))
    joint_values = np.array([[0.15] * 24], dtype=np.float32)

    expected_link_pose = np.array(
        [
            [-0.1538, -0.7761, 0.6115, 0.0726],
            [0.9513, 0.0511, 0.3041, 0.0148],
            [-0.2672, 0.6285, 0.7305, 0.4143],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    link_poses = robot_model.forward_kinematics_numpy(joint_values)
    assert np.allclose(link_poses[0, robot_model.first_spec.link_names.index("lftip")], expected_link_pose, atol=1e-4)


def test_topo_order_and_batch_dim():
    robot = Articulation.from_urdf_or_mjcf_paths("assets/robot_description/102730/mobility.urdf")
    # fmt: off
    expected_link_pose = np.array([
        [[ 1.0000,  0.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  0.0000,  1.0000]],

        [[-0.0000, -0.0000, -1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000, -0.0000,  0.0000],
        [ 0.0000,  0.0000,  0.0000,  1.0000]],

        [[-0.0000, -0.0000, -1.0000, -0.0000],
        [-1.0000,  0.0000,  0.0000, -0.0256],
        [ 0.0000,  1.0000, -0.0000,  0.2909],
        [ 0.0000,  0.0000,  0.0000,  1.0000]],

        [[-0.0000, -0.0000, -1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000, -0.0000,  0.0000],
        [ 0.0000,  0.0000,  0.0000,  1.0000]]
    ], dtype=np.float32)
    # fmt: on

    link_poses = robot.forward_kinematics(robot.get_packed_zero_joint_values(return_tensors="pt"), use_warp=False)
    assert np.allclose(link_poses.numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics(
        robot.get_packed_zero_joint_values(return_tensors="pt").unsqueeze(0), use_warp=False
    )
    assert np.allclose(link_poses[0].numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics(
        robot.get_packed_zero_joint_values(return_tensors="pt").unsqueeze(0).unsqueeze(0), use_warp=False
    )
    assert np.allclose(link_poses[0, 0].numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics(robot.get_packed_zero_joint_values(return_tensors="pt"), use_warp=True)
    assert np.allclose(link_poses.numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics(
        robot.get_packed_zero_joint_values(return_tensors="pt").unsqueeze(0), use_warp=True
    )
    assert np.allclose(link_poses[0].numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics(
        robot.get_packed_zero_joint_values(return_tensors="pt").unsqueeze(0).unsqueeze(0), use_warp=True
    )
    assert np.allclose(link_poses[0, 0].numpy(), expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics_numpy(robot.get_packed_zero_joint_values(return_tensors="np"))
    assert np.allclose(link_poses, expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics_numpy(robot.get_packed_zero_joint_values(return_tensors="np").reshape(1, -1))
    assert np.allclose(link_poses[0], expected_link_pose, atol=1e-4)

    link_poses = robot.forward_kinematics_numpy(
        robot.get_packed_zero_joint_values(return_tensors="np").reshape(1, 1, -1)
    )
    assert np.allclose(link_poses[0, 0], expected_link_pose, atol=1e-4)


def test_multi_arti():
    arti_specs = []
    arti_specs.append(ArticulationSpec("assets/robot_description/panda.urdf"))
    arti_specs.append(ArticulationSpec("assets/robot_description/shadow_hand_right.urdf"))
    arti_specs.append(
        ArticulationSpec(
            "assets/robot_description/kuka_iiwa14.xml",
            mjcf_assets={
                "link_0.obj": "",
                "link_1.obj": "",
                "link_2_orange.obj": "",
                "link_2_grey.obj": "",
                "link_3.obj": "",
                "band.obj": "",
                "kuka.obj": "",
                "link_4_orange.obj": "",
                "link_4_grey.obj": "",
                "link_5.obj": "",
                "link_6_orange.obj": "",
                "link_6_grey.obj": "",
                "link_7.obj": "",
            },
        )
    )
    arti = Articulation(arti_specs)
    joint_values = torch.tensor(
        [
            *[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02],
            *[0.15] * 24,
            *[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1],
        ],
        dtype=torch.float32,
    )
    joint_values.requires_grad_(True)
    link_poses = arti.forward_kinematics(joint_values.unsqueeze(0))
    expected_link_pose = torch.tensor(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(link_poses[0, arti.specs[0].num_links - 1], expected_link_pose, atol=1e-4)
    expected_link_pose = torch.tensor(
        [
            [-0.1538, -0.7761, 0.6115, 0.0726],
            [0.9513, 0.0511, 0.3041, 0.0148],
            [-0.2672, 0.6285, 0.7305, 0.4143],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(
        link_poses[0, arti.get_link_first_indices()[1] + arti.specs[1].link_names.index("lftip")],
        expected_link_pose,
        atol=1e-4,
    )
    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)

    link_poses = arti.forward_kinematics(joint_values)
    assert torch.allclose(link_poses[-3], expected_link_pose, atol=1e-4)

    link_poses = arti.forward_kinematics(joint_values.unsqueeze(0))
    indices = [
        *range(arti.get_link_first_indices()[1], arti.get_link_first_indices()[2]),
        arti.total_num_links - 1,
    ]
    link_poses[:, indices, :3, :3].abs().sum().backward()
    grad = joint_values.grad.clone()  # type: ignore

    # fmt: off
    panda_expected = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    shadow_expected = torch.tensor([25.4212, 34.2540, -0.8519, 3.3568, 2.0163, 1.0683, -0.8519, 3.3568,
                                  2.0163, 1.0683, 7.9247, 3.8035, 2.2961, 1.2243, 6.8456, 7.5744,
                                  2.8183, 2.0165, 1.0392, 3.0932, 7.3272, 5.6045, -0.1056, -0.3911])
    kuka_expected = torch.tensor([0.4059, 1.4686, 0.3498, -1.4969, 0.3350, 1.4344, 0.4556])
    # fmt: on

    assert torch.allclose(grad[:8], panda_expected, atol=1e-3)
    assert torch.allclose(grad[8:32], shadow_expected, atol=1e-3)
    assert torch.allclose(grad[32:], kuka_expected, atol=1e-3)

    # Test with use_warp=False
    link_poses = arti.forward_kinematics(joint_values.unsqueeze(0), use_warp=False)
    expected_link_pose = torch.tensor(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(link_poses[0, arti.specs[0].num_links - 1], expected_link_pose, atol=1e-4)
    expected_link_pose = torch.tensor(
        [
            [-0.1538, -0.7761, 0.6115, 0.0726],
            [0.9513, 0.0511, 0.3041, 0.0148],
            [-0.2672, 0.6285, 0.7305, 0.4143],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(
        link_poses[0, arti.get_link_first_indices()[1] + arti.specs[1].link_names.index("lftip")],
        expected_link_pose,
        atol=1e-4,
    )
    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)

    link_poses = arti.forward_kinematics(joint_values, use_warp=False)
    assert torch.allclose(link_poses[-3], expected_link_pose, atol=1e-4)

    link_poses = arti.forward_kinematics(joint_values.unsqueeze(0), use_warp=False)
    indices = [
        *range(arti.get_link_first_indices()[1], arti.get_link_first_indices()[2]),
        arti.total_num_links - 1,
    ]
    joint_values.grad = None  # Reset gradients
    link_poses[:, indices, :3, :3].abs().sum().backward()
    grad = joint_values.grad.clone()  # type: ignore

    assert torch.allclose(grad[:8], panda_expected, atol=1e-3)
    assert torch.allclose(grad[8:32], shadow_expected, atol=1e-3)
    assert torch.allclose(grad[32:], kuka_expected, atol=1e-3)


def test_root_poses_grad():
    device = "cpu"
    arti = Articulation(ArticulationSpec(urdf_or_mjcf_path="assets/robot_description/panda.urdf"), device=device)
    joint_values = torch.tensor([[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02]], dtype=torch.float32, device=device)
    root_poses = torch.eye(4).to(joint_values).unsqueeze(0)
    root_poses[0, 0, 3] = 0.1
    root_poses.requires_grad_(True)
    link_poses = arti.forward_kinematics(joint_values, root_poses=root_poses, use_warp=True)

    expected_link_pose = torch.tensor(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    expected_link_pose[0, 3] += 0.1
    assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
    link_poses[..., :3, 3].abs().sum().backward()
    root_poses_grad = root_poses.grad.clone()  # type: ignore

    expected_root_poses_grad = torch.tensor(
        [
            [
                [2.4668, 0.8038, 8.0780, 12.0000],
                [2.4668, 0.8038, 7.4120, 9.0000],
                [2.4668, 0.8038, 8.0780, 11.0000],
                [0.0000, 0.0000, 0.0000, 0.0000],
            ]
        ]
    )
    assert torch.allclose(root_poses_grad, expected_root_poses_grad, atol=1e-4)

    link_poses = arti.forward_kinematics(joint_values, root_poses=root_poses, use_warp=False)
    root_poses.grad = None
    link_poses[..., :3, 3].abs().sum().backward()
    root_poses_grad = root_poses.grad.clone()  # type: ignore
    assert torch.allclose(root_poses_grad, expected_root_poses_grad, atol=1e-4)


if __name__ == "__main__":
    test_basic()
    test_mjcf()
    test_multi_chain()
    test_numpy()
    test_topo_order_and_batch_dim()
    test_multi_arti()
