# maxheapq

This project implements heap data structure, specifically **max binary heap** described on [wikipedia](https://en.wikipedia.org/wiki/Binary_heap#Building_a_heap)

The purpose is to implement my own version and compare with 
already existing [heapq](https://docs.python.org/3/library/heapq.html), by default **heapq** implements min heap but we implement max heap here, hence the name **maxheapq**


in max heap, the element with highest priority or value will be at the first index of the underhood array, which can be seen as a complete binary tree, where **i** is index of Parent, with indices **2 * i+ 1**, **2 * i+ 2** as children of the parent

## Documentation
https://test.pypi.org/project/maxheapq-snow


## install and use package

install the package using below command to use locally on your machine

python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps maxheapq-snow

## Usage
Some basic operations:

    def max_heap.create_heap()
      - create an empty max heap 

    def size(self) -> int:
      - returns size or number of keys in the max heap

    def is_empty(self) -> bool:
      - returns True if no keys else False

    def find_max(self) -> key:
      - returns key with maximum value

    def insert(self, k: key):
     -  inserts new key k in the heap.

    def delete_max(self):
        - deletes max key or key at index 0 in the max heap array.

    def replace(self, k: key):
        - replace the first key or max key with the new key k .


    def increase_key(self, old_key: key, new_key: key):
        - search for the old key indices and then update with new key value
          if new_key > old_key


    def decrease_key(self, old_key: key, new_key: key):
       - search for the old key indices and then update with new key value
         if new_key < old_key


    def delete(self, del_key: key):
       - deletes keys that matches del_key


    def make_heap(array: list[int]) -> MaxHeap:
      - creates max heap from list of integers with time
        complexity O(n) according to Floyd's algorithm.

    def merge(heap1: MaxHeap, heap2: MaxHeap) -> MaxHeap:
      - returns a new max heap created by merging heap1 and heap2
