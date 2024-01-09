int pow(int b, int e) {
    int p = 1;
    while (e > 0) {
        p *= b;
        e--;
    }
    return p;
}