#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
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

Matrix multiply(const Matrix& A, const Matrix& B) {
    int n = A.size();
    Matrix C(n, vector<double>(n, 0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                C[i][j] += A[i][k] * B[k][j];
    return C;
}

int main(int argc, char* argv[]) {
    string fileA = argv[1];
    string fileB = argv[2];
    string fileC = argv[3];

    auto A = readMatrix(fileA);
    auto B = readMatrix(fileB);
    int n = A.size();

    auto start = chrono::high_resolution_clock::now();
    auto C = multiply(A, B);
    auto end = chrono::high_resolution_clock::now();

    writeMatrix(fileC, C);

    chrono::duration<double> elapsed = end - start;
    cout << "Размер: " << n << "x" << n << "\n";
    cout << "Время: " << elapsed.count() << " с\n";
    cout << "Операций: " << 2LL * n * n * n << "\n";
}