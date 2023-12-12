from util.util import iter_paired_chunks


def test__iter_paired_chunks__empty():
    assert list(iter_paired_chunks([], [], chunk_size=1)) == []


def test__iter_paired_chunks__first_empty():
    assert list(iter_paired_chunks([], [1, 2, 3], chunk_size=1)) == [
        ([], [1]),
        ([], [2]),
        ([], [3]),
    ]


def test__iter_paired_chunks__second_empty():
    assert list(iter_paired_chunks([1, 2, 3], [], chunk_size=1)) == [
        ([1], []),
        ([2], []),
        ([3], []),
    ]


def test__iter_paired_chunks__first_shorter():
    assert list(iter_paired_chunks([1, 2, 3], [4, 5, 6, 7, 8], chunk_size=3)) == [
        ([1, 2, 3], [4, 5, 6]),
        ([7, 8], []),
    ]


def test__iter_pair_chunks__second_shorter():
    assert list(iter_paired_chunks([1, 2, 3, 4, 5], [6, 7, 8], chunk_size=3)) == [
        ([1, 2, 3], [6, 7, 8]),
        ([4, 5], []),
    ]
