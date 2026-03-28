import numpy as np
import sys

def read_matrix(filename):
    with open(filename) as f:
        n = int(f.readline())
        mat = []
        for _ in range(n):
            row = list(map(float, f.readline().split()))
            mat.append(row)
    return np.array(mat)

def main():
    if len(sys.argv) < 4:
        print("Использование: python verify.py A.txt B.txt C.txt")
        return

    A = read_matrix(sys.argv[1])
    B = read_matrix(sys.argv[2])
    C_prog = read_matrix(sys.argv[3])

    C_numpy = np.dot(A, B)

    if np.allclose(C_prog, C_numpy, rtol=1e-10, atol=1e-12):
        print("Верификация успешна: результаты совпадают.")
    else:
        print("Ошибка: результаты различаются!")
        diff = np.abs(C_prog - C_numpy)
        print("Максимальное расхождение:", np.max(diff))

if __name__ == "__main__":
    main()