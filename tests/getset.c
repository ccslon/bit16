int array[10];
int get(int *g, int i) {
    return g[i];
}
void set(int *g, int i, int t) {
    g[i] = t;
}
int getarray(int i) {
    return array[i];
}
void setarray(int i, int t) {
    array[i] = t;
}
int getstack(int i) {
    int a[10];
    return a[i];
}
int getstack(int i, int t) {
    int a[10];
    a[i] = t;
}