int fib(int n) {
    if (n == 1) {
        return 0;
    } else if (n == 2) {
        return 1;
    } else {
        return fib(n-1) + fib(n-2);
    }
}

int fib2(int n) {
    switch(n) {
        case 1: return 0;
        case 2: return 1;
        default: return fib(n-1) + fib(n-2);
    }
}