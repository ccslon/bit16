int _div(int num, int den) {
    int quot = 0;
    int rem = 0;
    int i;
    for (i = 15; i >= 0; i--) {
        rem <<= 1;
        rem |= (num >> i) & 1;
        if (rem >= den) {
            rem -= den;
            quot |= (1 << i);
        }
    }
    return quot;
}