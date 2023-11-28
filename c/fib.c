#include "bit16lib.h"

int fib(int n) {
    switch (n) {
        case 1: return 0;
        case 2: return 1;
        default: return fib(n-1) + fib(n-2);
    }
}

void main() {
    int i;
    for (i = 1; i <= 10; i++) {
        printint(fib(i));
        put('\n');
    }
}