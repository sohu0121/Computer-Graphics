import numpy as np

M = np.arange(2, 27)
print(M)
print("\n")

M = M.reshape(5, 5)
print(M)
print("\n")

M[1:4, 1:4] = 0
print(M)
print("\n")

M = M @ M
print(M)
print("\n")

v = M[0]
ans = np.sqrt(np.sum(v @ v))
print(ans)
