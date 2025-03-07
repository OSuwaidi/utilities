import timeit
import numpy as np

# Approach 1
def approach_1(lengths):
    [np.random.randn(l) + 1 for l in lengths]


# Approach 2
def approach_2(lengths):
    [np.random.randn(l) + np.ones(l) for l in lengths]

# Input data
lengthsies = [10*i for i in range(1, 501)]

# Measure time
time_approach_1 = timeit.timeit(lambda: approach_1(lengthsies), number=100)
time_approach_2 = timeit.timeit(lambda: approach_2(lengthsies), number=100)


print(f"Approach 1 took {time_approach_1:.4f} seconds")
print(f"Approach 2 took {time_approach_2:.4f} seconds")
