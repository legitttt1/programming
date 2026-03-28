import subprocess
import os
import re

# Параметры
program = "matrix_omp.exe"
matrices_dir = "matrices"
results_dir = "results"
sizes = [200, 400, 800, 1200, 1600, 2000]
threads_list = [1, 2, 4, 8]

# Создаем папку для результатов
os.makedirs(results_dir, exist_ok=True)

# Проверки
if not os.path.exists(program):
    print(f"ERROR: Program '{program}' not found!")
    exit(1)

if not os.path.exists(matrices_dir):
    print(f"ERROR: Folder '{matrices_dir}' not found!")
    exit(1)

print("=" * 60)
print("Running experiments...")
print("=" * 60)

all_results = []

for size in sizes:
    print(f"\nSize: {size}x{size}")
    
    file_a = os.path.join(matrices_dir, f"A_{size}.txt")
    file_b = os.path.join(matrices_dir, f"B_{size}.txt")
    
    if not os.path.exists(file_a) or not os.path.exists(file_b):
        print(f"  WARNING: Matrix files not found, skipping...")
        continue
    
    for threads in threads_list:
        print(f"  {threads} threads...", end=" ", flush=True)
        
        file_c = os.path.join(results_dir, f"C_{size}_{threads}.txt")
        
        result = subprocess.run(
            [program, file_a, file_b, file_c, str(threads)],
            capture_output=True,
            text=True
        )
        
        # Парсим вывод
        time_sec = None
        gflops = None
        
        for line in result.stdout.split('\n'):
            if 'Time:' in line:
                # Ищем число
                numbers = re.findall(r'[\d]+\.?[\d]*', line)
                if numbers:
                    time_sec = float(numbers[0])
            if 'Performance:' in line:
                numbers = re.findall(r'[\d]+\.?[\d]*', line)
                if numbers:
                    gflops = float(numbers[0])
        
        # Если время 0 или очень маленькое (меньше 0.001), считаем его минимальным
        if time_sec is not None and time_sec < 0.0001:
            time_sec = 0.0001  # минимальное время для отображения
        
        if time_sec is not None:
            print(f"{time_sec:.4f} sec")
            all_results.append([size, threads, time_sec, gflops if gflops else 0])
        else:
            print("FAILED")
            print(f"    Program output: {result.stdout[:200]}")

# Сохраняем результаты
if all_results:
    with open("results.csv", "w") as f:
        f.write("Size,Threads,Time(sec),GFLOPS\n")
        for r in all_results:
            f.write(f"{r[0]},{r[1]},{r[2]:.6f},{r[3]:.2f}\n")
    
    # Выводим таблицу
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Size':<8}", end="")
    for t in threads_list:
        print(f"{t:>10}", end="")
    print()
    print("-" * 50)
    
    results_by_size = {}
    for r in all_results:
        size, threads, time_sec, _ = r
        if size not in results_by_size:
            results_by_size[size] = {}
        results_by_size[size][threads] = time_sec
    
    for size in sizes:
        if size in results_by_size:
            print(f"{size:<8}", end="")
            for t in threads_list:
                if t in results_by_size[size]:
                    print(f"{results_by_size[size][t]:>10.4f}", end="")
                else:
                    print(f"{'---':>10}", end="")
            print()
    
    # Ускорение
    print("\n\nSPEEDUP (T1/Tp):")
    print("-" * 50)
    print(f"{'Size':<8}", end="")
    for t in threads_list[1:]:
        print(f"{t:>10}", end="")
    print()
    print("-" * 50)
    
    for size in sizes:
        if size in results_by_size and 1 in results_by_size[size]:
            base = results_by_size[size][1]
            print(f"{size:<8}", end="")
            for t in threads_list[1:]:
                if t in results_by_size[size]:
                    speedup = base / results_by_size[size][t]
                    print(f"{speedup:>10.2f}x", end="")
                else:
                    print(f"{'---':>10}", end="")
            print()
    
    print("\n" + "=" * 60)
    print(f"Results saved to: results.csv")
    print(f"Matrix products saved to: {results_dir}/")
else:
    print("\nNo results collected!")

print("=" * 60)