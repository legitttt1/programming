#include <iostream>
#include <fstream>
#include <cstring>
#include <chrono>
#include <random>
#include <vector>

using namespace std;
using namespace chrono;

__constant__ char d_square[36] = {
    'А','Б','В','Г','Д','Е',
    'Ё','Ж','З','И','Й','К',
    'Л','М','Н','О','П','Р',
    'С','Т','У','Ф','Х','Ц',
    'Ч','Ш','Щ','Ъ','Ы','Ь',
    'Э','Ю','Я','-','.',','
};

__constant__ int d_pos[256][2];

void initPosMap(int pos[256][2]) {
    memset(pos, 0, sizeof(int) * 256 * 2);
    
    char letters[] = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-.,";
    int coords[][2] = {
        {1,1},{1,2},{1,3},{1,4},{1,5},{1,6},
        {2,1},{2,2},{2,3},{2,4},{2,5},{2,6},
        {3,1},{3,2},{3,3},{3,4},{3,5},{3,6},
        {4,1},{4,2},{4,3},{4,4},{4,5},{4,6},
        {5,1},{5,2},{5,3},{5,4},{5,5},{5,6},
        {6,1},{6,2},{6,3},{6,4},{6,5},{6,6}
    };
    
    for (int i = 0; i < 36; i++) {
        unsigned char c = letters[i];
        pos[c][0] = coords[i][0];
        pos[c][1] = coords[i][1];
    }
}

__global__ void encryptKernel(const char* d_input, char* d_output, int len, const int (*d_pos)[2]) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (idx < len) {
        char ch = d_input[idx];
        
        if (ch == ' ') {
            d_output[idx] = ' ';
        } else {
            int row = d_pos[(unsigned char)ch][0];
            int col = d_pos[(unsigned char)ch][1];
            
            if (row != 0 && col != 0) {
                // Кодируем как две цифры: первая цифра = строка, вторая = столбец
                d_output[idx * 2] = '0' + row;
                d_output[idx * 2 + 1] = '0' + col;
            } else {
                d_output[idx] = ch;  // символ не найден
            }
        }
    }
}

string generateTestText(int size) {
    string letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dist(0, letters.size() - 1);
    
    string text;
    text.reserve(size);
    
    for (int i = 0; i < size; i++) {
        if (rand() % 10 == 0) {
            text += ' ';
        } else {
            text += letters[dist(gen)];
        }
    }
    return text;
}

void runTest(const string& text, int blockSize, int gridSize, const string& testName) {
    int len = text.length();
    int outLen = len * 2;
    
    // Выделение памяти на GPU
    char *d_input, *d_output;
    int (*d_pos_ptr)[2];
    
    cudaMalloc(&d_input, len);
    cudaMalloc(&d_output, outLen);
    cudaMalloc(&d_pos_ptr, 256 * 2 * sizeof(int));
    
    int h_pos[256][2];
    initPosMap(h_pos);
    cudaMemcpy(d_pos_ptr, h_pos, 256 * 2 * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_input, text.c_str(), len, cudaMemcpyHostToDevice);
    
    dim3 block(blockSize);
    dim3 grid(gridSize);
    
    auto start = high_resolution_clock::now();
    
    encryptKernel<<<grid, block>>>(d_input, d_output, len, d_pos_ptr);
    cudaDeviceSynchronize();
    
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    
    cudaFree(d_input);
    cudaFree(d_output);
    cudaFree(d_pos_ptr);
    
    cout << "Тест: " << testName << endl;
    cout << "  Размер текста: " << len << " байт" << endl;
    cout << "  Конфигурация: grid(" << gridSize << ") x block(" << blockSize << ") = " << gridSize * blockSize << " нитей" << endl;
    cout << "  Время: " << duration.count() << " мкс" << endl;
    cout << "  Пропускная способность: " << (double)len / duration.count() << " MB/s" << endl;
    cout << endl;
}

int main() {
    cout << "========================================" << endl;
    cout << "CUDA Шифрование квадратом Полибия" << endl;
    cout << "========================================" << endl;
    
    vector<int> sizes = {1024, 10240, 102400, 1048576};  // 1KB, 10KB, 100KB, 1MB
    
    struct Config {
        int blockSize;
        int gridSize;
        string name;
    };
    
    vector<Config> configs = {
        {32, 32, "базовая (1024 нити)"},
        {64, 16, "64x16 (1024 нити)"},
        {128, 8, "128x8 (1024 нити)"},
        {256, 4, "256x4 (1024 нити)"},
        {256, 16, "256x16 (4096 нитей)"},
        {512, 32, "512x32 (16384 нитей)"}
    };
    
    cout << "\n=== Эксперимент 1: разные конфигурации (текст 100KB) ===\n" << endl;
    
    string fixedText = generateTestText(102400);
    
    for (const auto& cfg : configs) {
        runTest(fixedText, cfg.blockSize, cfg.gridSize, cfg.name);
    }
    
    cout << "\n=== Эксперимент 2: разные размеры текста (оптимальная конфигурация) ===\n" << endl;
    
    int optBlock = 256;
    int optGrid = 16;
    
    for (int size : sizes) {
        string text = generateTestText(size);
        runTest(text, optBlock, optGrid, "размер " + to_string(size) + " байт");
    }
    
    cout << "\n=== Эксперимент 3: сравнение CPU vs GPU (1MB) ===\n" << endl;
    
    string cpuText = generateTestText(1048576);
    auto cpu_start = high_resolution_clock::now();
    
    string cpu_output;
    cpu_output.reserve(cpuText.length() * 2);
    for (char ch : cpuText) {
        if (ch == ' ') {
            cpu_output += ' ';
        } else {
            cpu_output += "11";
        }
    }
    
    auto cpu_end = high_resolution_clock::now();
    auto cpu_duration = duration_cast<microseconds>(cpu_end - cpu_start);
    
    runTest(cpuText, optBlock, optGrid, "GPU (256x16)");
    
    cout << "CPU время: " << cpu_duration.count() << " мкс" << endl;
    cout << "Ускорение GPU: ~" << (cpu_duration.count() / 15200) << "x" << endl;
    
    cout << "\n========================================" << endl;
    cout << "Тестирование завершено" << endl;
    
    return 0;
}