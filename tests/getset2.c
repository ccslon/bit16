int array[10][10];
int get2(int **g, int i, int j) {
    return g[i][j];
}
void set2(int **g, int i, int j, int t) {
    g[i][j] = t;
}
int getarray2(int i, int j) {
    return array[i][j];
}
void setarray2(int i, int j, int t) {
    array[i][j] = t;
}
int getstack(int i, int j) {
    int a[5][5];
    return a[i][j];
}
int getstack(int i, int j, int t) {
    int a[5][5];
    a[i][j] = t;
}