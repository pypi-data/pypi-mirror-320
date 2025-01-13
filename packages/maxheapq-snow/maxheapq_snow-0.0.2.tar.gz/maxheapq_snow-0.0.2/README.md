# maxheapq

This project implements heap data structure, specifically **max binary heap** described on [wikipedia](https://en.wikipedia.org/wiki/Binary_heap#Building_a_heap)

The purpose is to implement my own version and compare with 
already existing [heapq](https://docs.python.org/3/library/heapq.html), by default **heapq** implements min heap but we implement max heap here, hence the name **maxheapq**


in max heap, the element with highest priority or value will be at the first index of the underhood array, which can be seen as a complete binary tree, where **i** is index of Parent, with indices **2 * i+ 1**, **2 * i+ 2** as children of the parent

## Documentation
https://pypi.org/project/maxheapq-snow/0.0.2/



## install and use package

install the package using below command to use locally on your machine

pip install maxheapq-snow==0.0.2

## API
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

## Usage

```

from maxheapq_snow import max_heap

# create an empty max heap
heap = max_heap.create_heap()

print(heap.array)  # []
print(heap.size())  # 0
print(heap.is_empty())  # True

# make a heap from a int list
heap = max_heap.make_heap([7, 2, 4, 1, 9, 3])

print(heap.array)  # [9, 7, 4, 1, 2, 3]
print(heap.size())  # 6
print(heap.is_empty())  # False



#    9
#  7   4
# 1 2 3

# insert and delete_max
heap.insert(5)  # key < root
print(heap.array)  # [9, 7, 5, 1, 2, 3, 4]

#    9
#  7   5
# 1 2 3 4

heap.delete_max()
print(heap.array)  # [7, 4, 5, 1, 2, 3]

#    7
#  4   5
# 1 2 3

heap.insert(10)  # key > root
print(heap.array)  # [10, 4, 7, 1, 2, 3, 5]


#    10
#  4   7
# 1 2 3 5

# replaces the root key of max heap
heap.replace(0)
print(heap.array)  # [7, 4, 5, 1, 2, 3, 0]


#    7
#  4   5
# 1 2 3 0

# increase key method below find all keys with 0 and replace it with 10
# in the heap
heap.increase_key(0, 10)
print(heap.find_max())  # 10
print(heap.array)  # [10, 4, 7, 1, 2,3,5]


#    10
#  4   7
# 1 2 3 5


# decrease key method below find all keys with 10 and replace it with 0
# in the heap
heap.decrease_key(10, 0)
print(heap.find_max())  # 7
print(heap.array)  # [7, 4, 5, 1, 2, 3, 0]


#    7
#  4   5
# 1 2 3 0

# delete deletes all keys with value 9
heap = max_heap.make_heap([7, 2, 4, 1, 9, 3, 9])
heap.delete(9)
print(heap.size())  # 5
print(heap.array)  # [7, 3, 4, 1, 2]


#    7
#  3   4
# 1 2

heap = max_heap.make_heap([9, 9, 9, 1, 9, 9, 9])
heap.delete(9)
print(heap.size())  # 1
print(heap.array)  # [1]


# 1

# merge two heaps
heap1 = max_heap.make_heap([7, 2, 4, 1, 9, 3])


#    9    
#  7   4  
# 1 2 3 

heap2 = max_heap.make_heap([-7, -1, 0, -4, -2, -3, 6])

#    6    
#  -1   0  
# -4 -2 -3 -7 

new_merged_heap = max_heap.merge(heap1,heap2)

#                  9                          
#         7                      6              
#   1          2          3          4        
# -1    0    -4    -2    -3    -7   

```