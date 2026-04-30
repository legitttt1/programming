import subprocess
import os
import re
from datetime import datetime

sizes = [200, 400, 800, 1200, 1600, 2000]
processes = [1, 2, 4, 8]

matrices_dir = "matrices"
results_dir = "results"

os.makedirs(results_dir, exist_ok=True)

print("=" * 60)
print("MPI Matrix Multiplication Experiments")
print("=" * 60)

if not os.path.exists("matrix_mpi.exe"):
    print("ERROR: matrix_mpi.exe not found!")
    exit(1)

all_results = []

for size in sizes:
    print(f"\nSize: {size}x{size}")
    
    file_a = f"{matrices_dir}/A_{size}.txt"
    file_b = f"{matrices_dir}/B_{size}.txt"
    
    if not os.path.exists(file_a) or not os.path.exists(file_b):
        print(f"  WARNING: Missing files for size {size}")
        continue
    
    for p in processes:
        print(f"  Processes: {p}...", end=" ", flush=True)
        
        file_c = f"{results_dir}/C_{size}_{p}.txt"
        
        try:
            result = subprocess.run(
                ["mpiexec", "-n", str(p), "matrix_mpi.exe", file_a, file_b, file_c],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            time_sec = None
            gflops = None
            
            for line in result.stdout.split('\n'):
                if "Time:" in line:
                    match = re.search(r'[\d\.]+', line)
                    if match:
                        time_sec = float(match.group(0))
                if "Performance:" in line:
                    match = re.search(r'[\d\.]+', line)
                    if match:
                        gflops = float(match.group(0))
            
            if time_sec:
                print(f"OK ({time_sec:.3f} sec)")
                all_results.append([size, p, time_sec, gflops])
            else:
                print("FAILED")
                
        except Exception as e:
            print(f"ERROR: {e}")

if all_results:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"mpi_results_{timestamp}.csv"
    
    with open(csv_file, "w") as f:
        f.write("Size,Processes,Time(sec),GFLOPS\n")
        for r in all_results:
            f.write(f"{r[0]},{r[1]},{r[2]:.6f},{r[3] if r[3] else 0:.2f}\n")
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Saved to: {csv_file}")