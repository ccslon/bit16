int pow(int base, int exp) {
    int p = 1;
    while (exp > 0) {
        p *= base;
        exp--;
    }
    return p;
}