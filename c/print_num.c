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

void main() {
    print_int(420);
}