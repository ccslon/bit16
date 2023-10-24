int fib(int n) {
    switch (n) {
        case 1: return 0;
        case 2: return 1;
        default: return fib(n-1) + fib(n-2);
    }
}