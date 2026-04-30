#include <iostream>
#include <fstream>
#include <vector>
#include <mpi.h>
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

Matrix multiplyMPI(const Matrix& A, const Matrix& B, int rank, int size) {
    int n = A.size();
    Matrix C(n, vector<double>(n, 0.0));
    
    int rows_per_proc = n / size;
    int start_row = rank * rows_per_proc;
    int end_row = (rank == size - 1) ? n : start_row + rows_per_proc;
    
    Matrix local_C(end_row - start_row, vector<double>(n, 0.0));
    
    for (int i = start_row; i < end_row; i++) {
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < n; k++) {
                sum += A[i][k] * B[k][j];
            }
            local_C[i - start_row][j] = sum;
        }
    }
    
    if (rank == 0) {
        for (int i = start_row; i < end_row; i++) {
            for (int j = 0; j < n; j++) {
                C[i][j] = local_C[i - start_row][j];
            }
        }
        
        for (int p = 1; p < size; p++) {
            int p_start = p * rows_per_proc;
            int p_end = (p == size - 1) ? n : p_start + rows_per_proc;
            int p_rows = p_end - p_start;
            
            vector<double> buffer(p_rows * n);
            MPI_Recv(buffer.data(), p_rows * n, MPI_DOUBLE, p, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            
            for (int i = 0; i < p_rows; i++) {
                for (int j = 0; j < n; j++) {
                    C[p_start + i][j] = buffer[i * n + j];
                }
            }
        }
    } else {
        vector<double> buffer(local_C.size() * n);
        for (int i = 0; i < local_C.size(); i++) {
            for (int j = 0; j < n; j++) {
                buffer[i * n + j] = local_C[i][j];
            }
        }
        MPI_Send(buffer.data(), local_C.size() * n, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }
    
    return C;
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (argc < 4) {
        if (rank == 0) {
            cerr << "Usage: mpiexec -n N " << argv[0] 
                 << " <matrix_A> <matrix_B> <matrix_C>" << endl;
        }
        MPI_Finalize();
        return 1;
    }
    
    string fileA = argv[1];
    string fileB = argv[2];
    string fileC = argv[3];
    
    Matrix A, B;
    
    if (rank == 0) {
        A = readMatrix(fileA);
        B = readMatrix(fileB);
        cout << "Matrix size: " << A.size() << "x" << A.size() << endl;
        cout << "Using processes: " << size << endl;
    }
    
    int n = 0;
    if (rank == 0) n = A.size();
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    if (rank != 0) {
        A.resize(n, vector<double>(n));
        B.resize(n, vector<double>(n));
    }
    
    for (int i = 0; i < n; i++) {
        MPI_Bcast(A[i].data(), n, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        MPI_Bcast(B[i].data(), n, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    }
    
    double start = MPI_Wtime();
    Matrix C = multiplyMPI(A, B, rank, size);
    double end = MPI_Wtime();
    
    if (rank == 0) {
        writeMatrix(fileC, C);
        double elapsed = end - start;
        long long operations = 2LL * n * n * n;
        
        cout << "Time: " << elapsed << " sec" << endl;
        cout << "Operations: " << operations << endl;
        cout << "Performance: " << (operations / elapsed / 1e9) << " GFLOPS" << endl;
    }
    
    MPI_Finalize();
    return 0;
}