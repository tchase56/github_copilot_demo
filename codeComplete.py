######################################
# Examples
######################################

# Write a function that computes the pythagorean theorem for the lengths of the two legs of a right triangle

# original function
def add_floats(a: float, b: float) -> float:
    return a + b


######################################
# Examples with completions
######################################

# Write a function that computes the pythagorean theorem for the lengths of the two legs of a right triangle
def pythagorean_theorem(a: float, b: float) -> float:
    """
    Computes the length of the hypotenuse of a right triangle given the lengths of the two legs.

    Args:
        a (float): Length of the first leg.
        b (float): Length of the second leg.

    Returns:
        float: Length of the hypotenuse.
    """
    return (a**2 + b**2)**0.5

# Function where docstring has been completed using "code completions"
def add_floats(a: float, b: float) -> float:
    """
    Adds two floating point numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of the two numbers.
    """
    return a + b