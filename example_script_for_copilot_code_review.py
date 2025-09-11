import matplotlib.pyplot as plt

def area_circle(radius: float) -> float:
    """
    Calculate the area of a circle given its radius.
    
    Args:
        radius (float): The radius of the circle.
    
    Returns:
        float: The area of the circle.
    """
    return 3.14 * radius * radius

def dot_product(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate the dot product of two vectors.

    Args:
        vec_a (list of float): The first vector.
        vec_b (list of float): The second vector.

    Returns:
        float: The dot product of the two vectors.
    """
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

def area_of_circle(radius: float) -> float:
    """
    Calculate the area of a circle given its radius.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The area of the circle.
    """
    return math.pi * radius * radius
            
        