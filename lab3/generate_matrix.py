import numpy as np
import os

os.makedirs("matrices", exist_ok=True)

sizes = [200, 400, 800, 1200, 1600, 2000]

print("Generating matrices...")

for n in sizes:
    print(f"  {n}x{n}...", end=" ", flush=True)
    
    A = np.random.rand(n, n).astype(np.float64)
    B = np.random.rand(n, n).astype(np.float64)
    
    with open(f"matrices/A_{n}.txt", 'w') as f:
        f.write(f"{n}\n")
        for row in A:
            f.write(" ".join(map(str, row)) + "\n")
    
    with open(f"matrices/B_{n}.txt", 'w') as f:
        f.write(f"{n}\n")
        for row in B:
            f.write(" ".join(map(str, row)) + "\n")
    
    print("OK")

with open("matrices/A_test.txt", 'w') as f:
    f.write("2\n1 2\n3 4\n")
with open("matrices/B_test.txt", 'w') as f:
    f.write("2\n5 6\n7 8\n")

print("\nDone! Matrices saved to 'matrices/' folder")