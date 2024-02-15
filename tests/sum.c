int sqr(int n) {
    return n * n;
}

int sum(int n, int (*f)(int)) {
    int s = 0, i;
    for (i = 0; i < n; i++) {
        s += (*f)(i);
    }
    return s;
}