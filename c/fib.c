#include <stdio.h>
#include <string.h>

struct div_t {
    int div;
    int mod;
};

struct div_t div(int n, int d) {
    struct div_t ans;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans.div = q;
    ans.mod = n;
    return ans;
}

void print_int(int num) {
    struct div_t ans;
    char buffer[5];
    int i;
    for (i = 0; i < 5; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = div(num, 10);
        buffer[i] = '0' + ans.mod;
        i++;
        num = ans.div;
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