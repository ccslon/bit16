int myfoo(int a, int b) {
    return a + b;
}

void main() {
    int (*foo[4])(int a, int b) = {myfoo,myfoo,myfoo,myfoo};
    int *bar(int, int);
    int i;
    for (i = 0; i < 4; i++) {
        (*foo)[i](i, i+1);
    }
}