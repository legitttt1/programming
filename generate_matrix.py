import numpy as np
import os

# Создаем папку для матриц
os.makedirs("matrices", exist_ok=True)

sizes = [200, 400, 800, 1200, 1600, 2000]

print("Generating matrices...")

for n in sizes:
    print(f"  {n}x{n}...", end=" ", flush=True)
    
    # Генерируем случайные матрицы
    A = np.random.rand(n, n).astype(np.float64)
    B = np.random.rand(n, n).astype(np.float64)
    
    # Сохраняем в папку matrices
    with open(f"matrices/A_{n}.txt", 'w') as f:
        f.write(f"{n}\n")
        for row in A:
            f.write(" ".join(map(str, row)) + "\n")
    
    with open(f"matrices/B_{n}.txt", 'w') as f:
        f.write(f"{n}\n")
        for row in B:
            f.write(" ".join(map(str, row)) + "\n")
    
    print("OK")

print("\nDone! Matrices saved to 'matrices/' folder")