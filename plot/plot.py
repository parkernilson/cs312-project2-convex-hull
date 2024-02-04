import numpy as np
import matplotlib.pyplot as plt

# x = np.linspace(0, 2 * np.pi, 10)
# y = np.sin(x)

# x = (
#     [10] * 5
#     + [100] * 5
#     + [1000] * 5
#     + [10000] * 5
#     + [100000] * 5
#     + [500000] * 5
#     + [1000000] * 5
# )
x = np.linspace(10, 1000000, 35)

empirical_runtimes = (
    # 10
    [0, 0, 0, 0, 0]
    # 100
    + [0.002, 0.002, 0.003, 0.003, 0.002]
    # 1000
    + [0.018, 0.016, 0.018, 0.018, 0.018]
    # 10000
    + [0.088, 0.091, 0.091, 0.092, 0.091]
    # 100000
    + [0.816, 0.839, 0.819, 0.816, 0.848]
    # 500000
    + [5.149, 5.239, 5.222, 5.373, 5.384]
    # 1000000
    + [10.633, 10.631, 10.950, 11.164, 10.657]
)

# c = 0.000002
# c = 1
# theoretical_runtimes = list(map(lambda v: np.log(v) * v * c, x))

fig, ax = plt.subplots()
ax.set_title('Convex Hull Run Time Complexity')
ax.set_yscale("log")
ax.plot(x, empirical_runtimes)
# ax.plot(x, theoretical_runtimes)
plt.show()
