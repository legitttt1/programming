import os
import shutil

# Удаляем папку с результатами
if os.path.exists("results"):
    shutil.rmtree("results")
    print("Deleted 'results' folder")

# Удаляем файл результатов
if os.path.exists("results.csv"):
    os.remove("results.csv")
    print("Deleted results.csv")

print("Cleanup done!")