import timeit
import os

# Approach 1
def approach_1(cmd):
    for path in filter(os.path.isdir, os.environ["PATH"].split(os.pathsep)):  # "os.pathsep" is ";" for Windows and ":" for Unix)
        if os.path.isfile((full_path := os.path.join(path, cmd))) and os.access(full_path, os.X_OK):  # if file exists and is an executable...
            return full_path


# Approach 2
def approach_2(cmd):
    for path in os.environ["PATH"].split(os.pathsep):  # "os.pathsep" is ";" for Windows and ":" for Unix)
        if os.path.isdir(path) and os.path.isfile((full_path := os.path.join(path, cmd))) and os.access(full_path, os.X_OK):  # if file exists and is an executable...
            return full_path

# Input data

# Measure time
time_approach_1 = timeit.timeit(lambda: approach_1("ls"), number=1000)
time_approach_2 = timeit.timeit(lambda: approach_2("ls"), number=1000)


print(f"Approach 1 took {time_approach_1:.4f} seconds")
print(f"Approach 2 took {time_approach_2:.4f} seconds")
