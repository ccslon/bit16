#include "bit16lib.h"

int fib(const int n) { //36.24
    switch (n) {
        case 1: return 0;
        case 2: return 1;
        default: return fib(n-1) + fib(n-2);
    }
}

int dofib(const int n, const int a, const int b) {
    switch (n) {
        case 1: return a;
        case 2: return b;
        default: {
            return dofib(n-1, b, a+b);
        }
    }
}
int tailfib(const int n) {
    return dofib(n, 0, 1);
}

void fastfib(const int n) { //12.30, 11.39
    int i; int n1; int n2; int f;
    for (i = 1; n > 0 && i <= n; i++) {
        switch (i) {
            case 1: {
                f = n1 = 0;
                break;
            }
            case 2: {
                f = n2 = 1;
                break;
            }
            default: {
                f = n1 + n2;
                n1 = n2;
                n2 = f;
            }
        }
        printint(f);
        put('\n');
    }
}

void main() {
    int i;
    
    /* for (i = 1; i <= 10; i++) {
        printint(fib(i));
        put('\n');
    } */
    for (i = 1; i <= 10; i++) {
        printint(tailfib(i));
        put('\n');
    }
    
    ///fastfib(10);
}