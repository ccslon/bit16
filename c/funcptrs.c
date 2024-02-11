int mycmp(int a, int b) {
    return a - b;
}

void sort(int* v, int n, int (*cmp)(int, int)) {
    mycmp(33, 55);
    (*cmp)(v[0], v[n-1]);
}
struct Cat {
    char* name;
    int age;
};

void main() {
    int b[3];
    sort(b, 3, &mycmp);
}