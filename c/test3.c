int div(int n, int d) {
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    return q;
}