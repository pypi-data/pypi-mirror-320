"""
max_heap.py

A max-heap implemetation in python.
https://en.wikipedia.org/wiki/max_heap(data_structure)

"""

import copy

# Supports heap with key(s) type as only int
key = int
arr_idx = int


class MaxHeap:

    def __init__(self):
        """construct inital heap with empty keys"""
        self.array = []

    def size(self) -> int:
        """returns number of keys in the heap"""
        return len(self.array)

    def is_empty(self) -> bool:
        """returns True if no keys else False"""
        return len(self.array) == 0

    def find_max(self) -> key:
        """returns first key from the heap array, as max key
        is always at index 0"""
        try:
            return self.array[0]
        except IndexError:
            raise IndexError("cannot find max on empty heap")

    def insert(self, k: key):
        """insert the new key at the end of the array and then move
        it upwards in the binary tree"""
        self.array.append(k)
        self._sift_up(len(self.array) - 1)

    def delete_max(self):
        """replace the first key with the last key in the heap array, as max key
        is always at index 0, pop the last key and then move it downwards
        in the binary tree"""
        try:
            max_key = self.array[0]
            last = self.array.pop()
            self.replace(last)
        except IndexError:
            raise IndexError("cannot pop on empty heap")

    def replace(self, k: key):
        """replace the first key or max key with the new key then move it downwards
        in the binary tree"""
        try:
            if k < self.array[0]:
                self.array[0] = k
                self._sift_down()
            else:
                self.array[0] = k
        except IndexError:
            raise IndexError("cannot replace on empty heap, use push instead")

    def increase_key(self, old_key: key, new_key: key):
        """search for the old key index and then update with new key then move it upwards
        in the binary tree"""

        if old_key > new_key:
            raise ValueError("new key cannot be smaller than old key")
        for idx, key in enumerate(self.array):
            if key == old_key:
                self.array[idx] = new_key
                self._sift_up(idx)

    def decrease_key(self, old_key: key, new_key: key):
        """search for the old key index and then update with new key then move it downwards
        in the binary tree"""
        if old_key < new_key:
            raise ValueError("old key cannot be smaller than new key")
        for idx, key in enumerate(self.array):
            if key == old_key:
                self.array[idx] = new_key
                self._sift_down(idx)

    def delete(self, del_key: key):
        """delete the key(s) in the heap, we increase the keys that gets deleted with max value
        and sift up in the binary tree and then delete the max, number of times we increase
        the keys"""

        try:
            max_key = self.array[0]
        except:
            IndexError("cannot _delete on empty heap")

        while del_key == max_key:
            self.delete_max()
            if self.find_max() != max_key:
                return

        num_del_keys = 0
        for idx, key in enumerate(self.array):
            if key == del_key:
                num_del_keys = num_del_keys + 1
                self.increase_key(key, max_key)

        while num_del_keys > 0:
            self.delete_max()
            num_del_keys = num_del_keys - 1

    def _swap_keys(self, i: arr_idx, j: arr_idx):
        """swap the keys at indices i and j"""
        t_key = self.array[i]
        self.array[i] = self.array[j]
        self.array[j] = t_key

    def _sift_up(self, idx: arr_idx):
        """move the key upwards starting at index idx recursively until its parent is greater than itself
        if no parent is greater, key becomes max or root in binary tree"""
        if idx == 0:
            return
        parent_idx = int(idx / 2) if idx % 2 == 1 else int(idx / 2 - 1)
        if self.array[idx] > self.array[parent_idx]:
            self._swap_keys(idx, parent_idx)
            self._sift_up(parent_idx)
        else:
            return

    def _sift_down(self, idx: arr_idx = 0):
        """move the key downwards starting at index idx recursively until its children is smaller
        than itself if no children is smaller, key becomes one of the leaf in binary tree
        """
        try:
            left_idx = 2 * idx + 1
            right_idx = 2 * idx + 2
            child_idx = (
                left_idx if self.array[left_idx] >= self.array[right_idx] else right_idx
            )
            if self.array[idx] < self.array[child_idx]:
                self._swap_keys(idx, child_idx)
                self._sift_down(child_idx)

        except IndexError:
            return


"""Operations related to creation of binary heap"""


def create_heap() -> MaxHeap:
    """creates empty heap"""
    return MaxHeap()


def make_heap(array: list[int]) -> MaxHeap:
    """creates heap with time complexity O(n) Floyd's algorithm.

    according to J. W. J. Williams  adding element at the end of one heap array of size n
    and siftup will result in time complexity nlogn, where in the worst case
    every last added key will be max key, so sift up will result in logn,
    hence for n elements worst case is n * log n.

    acording to Floyd, we start from nodes at last complete level in the binary
    tree representation and keep we sift down parent with lower values than children,
    for some height k starting from bottom of the tree leaving leaves of the tree,
    time complexity will be sum of k * (number of elements at height k ), which reduces height for
    sift down for most of elements, as most number of elements are concentrated at lower levels, so sum
    from k = 1 to h-1, i. k from 1 to log n , k * (2 **(log n - k)), for larger n s
    is O(n)


    """
    heap = MaxHeap()
    heap.array = array
    len_arr = len(heap.array)
    i = int(len_arr / 2) if len_arr % 2 == 1 else len_arr / 2 - 1
    i = len(heap.array) - 1
    while i >= 0:
        heap._sift_down(i)
        i -= 1
    return heap


# Merge two heaps,
# heap1 and heap2 to create a new heap
def merge(heap1: MaxHeap, heap2: MaxHeap) -> MaxHeap:
    """returns a new heap created from heap1 and heap2"""
    if heap2.is_empty():
        new_heap = copy.deepcopy(heap1)
        return new_heap
    if heap1.is_empty():
        new_heap = copy.deepcopy(heap2)
        return new_heap
    heap = make_heap(heap1.array + heap2.array)
    return heap
