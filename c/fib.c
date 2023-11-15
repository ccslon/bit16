#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void print_int(int num) {
    div_t ans;
    char buffer[5];
    int i;
    for (i = 0; i < 5; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = div(num, 10);
        buffer[i] = '0' + ans.rem;
        i++;
        num = ans.quot;
    } while (num > 0);
    strrev(&buffer);
    puts(&buffer);
}

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
        print_int(fib(i));
    }
}