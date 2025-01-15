import numpy as np
from fastdev.utils.struct import list_to_packed_numpy, list_to_padded_numpy


def test_list_to_padded_numpy():
    x = [np.array([1, 2, 3]), np.array([4, 5]), np.array([6, 7, 8, 9])]
    padded = list_to_padded_numpy(x)
    assert padded.shape == (3, 4)
    assert np.all(padded == np.array([[1, 2, 3, 0], [4, 5, 0, 0], [6, 7, 8, 9]]))

    x = [np.array([[1, 2, 3], [11, 12, 13]]), np.array([[4, 5], [44, 45]]), np.array([[6, 7, 8, 9], [66, 67, 68, 69]])]
    padded = list_to_padded_numpy(x)
    assert padded.shape == (3, 2, 4)
    assert np.all(
        padded
        == np.array(
            [
                [[1, 2, 3, 0], [11, 12, 13, 0]],
                [[4, 5, 0, 0], [44, 45, 0, 0]],
                [[6, 7, 8, 9], [66, 67, 68, 69]],
            ]
        )
    )

    x = [np.array([[1, 2, 3], [11, 12, 13]]), np.array([[4, 5], [44, 45]]), np.array([[6, 7, 8, 9], [66, 67, 68, 69]])]
    padded = list_to_padded_numpy(x, pad_size=[3, 4])
    assert padded.shape == (3, 3, 4)
    assert np.all(
        padded
        == np.array(
            [
                [[1, 2, 3, 0], [11, 12, 13, 0], [0, 0, 0, 0]],
                [[4, 5, 0, 0], [44, 45, 0, 0], [0, 0, 0, 0]],
                [[6, 7, 8, 9], [66, 67, 68, 69], [0, 0, 0, 0]],
            ]
        )
    )

    padded = list_to_padded_numpy(x, pad_value=1)
    assert np.all(
        padded
        == np.array(
            [
                [[1, 2, 3, 1], [11, 12, 13, 1]],
                [[4, 5, 1, 1], [44, 45, 1, 1]],
                [[6, 7, 8, 9], [66, 67, 68, 69]],
            ]
        )
    )

    x = [np.array([[1, 2, 3], [11, 12, 13]]), np.array([[4, 5, 6], [44, 45, 46]]), np.array([[7, 8, 9], [77, 78, 79]])]
    padded = list_to_padded_numpy(x, equisized=True)
    assert padded.shape == (3, 2, 3)
    assert np.all(
        padded
        == np.array(
            [
                [[1, 2, 3], [11, 12, 13]],
                [[4, 5, 6], [44, 45, 46]],
                [[7, 8, 9], [77, 78, 79]],
            ]
        )
    )


def test_list_to_packed_numpy():
    x = [np.array([1, 2, 3]), np.array([4, 5]), np.array([6, 7, 8, 9])]
    packed, num_items, item_packed_first_idx, item_packed_to_list_idx = list_to_packed_numpy(x)
    assert packed.shape == (9,)
    assert np.all(packed == np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]))
    assert np.all(num_items == np.array([3, 2, 4]))
    assert np.all(item_packed_first_idx == np.array([0, 3, 5]))
    assert np.all(item_packed_to_list_idx == np.array([0, 0, 0, 1, 1, 2, 2, 2, 2]))

    x = [
        np.array([[1, 11], [2, 22], [3, 33]]),
        np.array([[4, 44], [5, 55]]),
        np.array([[6, 66], [7, 77], [8, 88], [9, 99]]),
    ]
    packed, num_items, item_packed_first_idx, item_packed_to_list_idx = list_to_packed_numpy(x)
    assert packed.shape == (9, 2)
    assert np.all(packed == np.array([[1, 11], [2, 22], [3, 33], [4, 44], [5, 55], [6, 66], [7, 77], [8, 88], [9, 99]]))
    assert np.all(num_items == np.array([3, 2, 4]))
    assert np.all(item_packed_first_idx == np.array([0, 3, 5]))
    assert np.all(item_packed_to_list_idx == np.array([0, 0, 0, 1, 1, 2, 2, 2, 2]))


if __name__ == "__main__":
    test_list_to_packed_numpy()
