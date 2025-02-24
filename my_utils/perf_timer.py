import timeit

# Approach 1
def approach_1(A):

    return A


# Approach 2
def approach_2(A):

    return A

# Input data
import numpy as np
A = np.random.randn(np.random.randint(50), np.random.randint(50))

# Measure time
time_approach_1 = timeit.timeit(lambda: approach_1(A.copy()), number=1000)
time_approach_2 = timeit.timeit(lambda: approach_2(A.copy()), number=1000)


print(f"Approach 1 took {time_approach_1:.4f} seconds")
print(f"Approach 2 took {time_approach_2:.4f} seconds")
