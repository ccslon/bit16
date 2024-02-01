int _mod(int num, int den) {
    int rem = 0;
    int i;
    for (i = 15; i >= 0; i--) {
        rem <<= 1;
        rem |= (num >> i) & 1;
        if (rem >= den) {
            rem -= den;
        }
    }
    return rem;
}