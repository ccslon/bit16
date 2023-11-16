int pow(int base, int exp) {
    int pow = 1;
    while (exp > 0) {
        pow *= base;
        exp--;
    }
    return pow;
}