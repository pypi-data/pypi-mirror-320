"""
script to print heap array as bianry tree 
"""

# import math
# from maxheapq_snow.max_heap import *


# def print_bt(heap: MaxHeap):
#     """ prints heap array as binary tree"""
#     heap_size = heap.size()
#     height_float = math.log(heap_size + 1, 2)
#     height = int(math.ceil(height_float))
#     final_list = list()
#     final_level_len = 2 ** (height - 1)
#     initial_list = list()
#     i = 0
#     while i < final_level_len:
#         initial_list.append(3 * i)
#         i = i + 1
#     final_list.append(initial_list)

#     while True:
#         new_list = list()
#         first_list = final_list[0]
#         len_first_list = len(first_list)
#         if len_first_list == 1:
#             break
#         for i in range(0, len_first_list, 2):
#             k = (first_list[i] + first_list[i + 1]) / 2
#             new_list.append(int(k))
#         final_list.insert(0, new_list)
#     print()
#     print(final_list)
#     print()
#     j = 0
#     w = 3 * final_level_len
#     for i in range(0, height):
#         first_list = final_list[i]
#         print_list = list()
#         for c in range(0, w):
#             if c in first_list:
#                 if j < heap_size:
#                     print_list.append(heap.array[j])
#                     j = j + 1
#                 else:
#                     break
#             else:
#                 print_list.append("  ")

#         buf_str = str()
#         for elem in print_list:
#             if elem is int and elem > 0:
#                 buf_str = buf_str + " "+str(elem)
#                 continue
#             buf_str = buf_str + str(elem)
#         print(buf_str)
