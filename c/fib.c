#include <stdio.h>

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
void main() {
    int i;
    printf("Fib! %d %d\n", 0, 1);
    for (i = 1; i <= 10; i++)
        printf("%d\n", tailfib(i));    
}