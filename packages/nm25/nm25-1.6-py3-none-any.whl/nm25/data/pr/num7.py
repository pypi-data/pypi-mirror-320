# ## Круги Гершгорина
# 
# Теорема Гершгорина утрверждает, что все собственные значения $\lambda_i, i = 1,\dots,n$ находятся в объединении кругов Гершкорина $C_i$, где $C_i$ - окружность на комплексной плоскости с центром в $a_{ii}$ и радиусом $r = \sum\limits_{j\neq i}|a_{ij}|$
# 
# Более того, если круги не пересекаются, то они содержат по одному собственному значению внутри каждого круга.



import numpy as np
import matplotlib.pyplot as plt




fig, ax = plt.subplots(1, 1)
A = np.array(
    [
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
    ]
)

ev = np.linalg.eigvals(A)

for i in range(A.shape[0]):
    #rad = sum(abs(A[i, j]) for j in range(A.shape[1]) if j != i)
    rad = sum(abs(A[i])) - abs(A[i, i])

    crc = plt.Circle(
        (A[i, i].real, A[i, i].imag),
        radius=rad,
        fill=False,
    )

    ax.add_patch(crc)


plt.scatter(ev.real, ev.imag, color="r", label="Собственные значения")
plt.axis("equal")
plt.legend()