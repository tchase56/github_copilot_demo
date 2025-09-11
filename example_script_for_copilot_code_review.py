import statistics

def define_area_of_circle(radius):
    return math.pi * radius ** 2

def define_area_circle(radius):
    return 3.14 * radius * radius

def dot_product(vec_a, vec_b):
    ans = None
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of the same length")
    for i in range(len(vec_a)):
        for j in range(len(vec_b)):
            if i == j:
                if ans is None:
                    ans = vec_a[i] * vec_b[j]
                else:
                    ans += vec_a[i] * vec_b[j]
    return ans
            
        