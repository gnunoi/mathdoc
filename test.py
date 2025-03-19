from itertools import combinations

def generate_opposite_lists(lst):
    result = []
    n = len(lst)
    for k in range(1, n+1):  # k表示要改变的元素个数，从1到n
        for indices in combinations(range(n), k):  # 生成所有可能的k个元素的索引组合
            new_list = lst.copy()
            for idx in indices:
                new_list[idx] = -new_list[idx]
            result.append(new_list)
    return result

# 示例用法
original_list = [1, 2, 3]
opposite_lists = generate_opposite_lists(original_list)
print(opposite_lists)