#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <omp.h>
using namespace std;

using Matrix = vector<vector<double>>;

Matrix readMatrix(const string& filename) {
    ifstream file(filename);
    int n;
    file >> n;
    Matrix mat(n, vector<double>(n));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            file >> mat[i][j];
    return mat;
}

void writeMatrix(const string& filename, const Matrix& mat) {
    ofstream file(filename);
    int n = mat.size();
    file << n << "\n";
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++)
            file << mat[i][j] << " ";
        file << "\n";
    }
}

Matrix multiply(const Matrix& A, const Matrix& B, int num_threads) {
    int n = A.size();
    Matrix C(n, vector<double>(n, 0.0));
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for collapse(2) schedule(static)
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
        }
    }
    
    return C;
}

int main(int argc, char* argv[]) {
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " <matrix_A> <matrix_B> <matrix_C> <num_threads>" << endl;
        return 1;
    }
    
    string fileA = argv[1];
    string fileB = argv[2];
    string fileC = argv[3];
    int num_threads = atoi(argv[4]);
    
    int max_threads = omp_get_max_threads();
    cout << "Max available threads: " << max_threads << endl;
    cout << "Using threads: " << num_threads << endl;
    
    auto A = readMatrix(fileA);
    auto B = readMatrix(fileB);
    int n = A.size();
    
    if (n != B.size()) {
        cerr << "Error: matrix sizes do not match!" << endl;
        return 1;
    }
    
    double start = omp_get_wtime();
    auto C = multiply(A, B, num_threads);
    double end = omp_get_wtime();
    
    writeMatrix(fileC, C);
    
    double elapsed = end - start;
    long long operations = 2LL * n * n * n;
    
    cout << "Matrix size: " << n << "x" << n << endl;
    cout << "Time: " << elapsed << " sec" << endl;
    cout << "Operations: " << operations << endl;
    cout << "Performance: " << (operations / elapsed / 1e9) << " GFLOPS" << endl;
    
    return 0;
}