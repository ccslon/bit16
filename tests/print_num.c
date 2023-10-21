#include <stdio.h>
#include <string.h>

struct DivMod {
    int div;
    int mod;
};

struct DivMod* divmod(int n, int d) {
    struct DivMod* ans;
    ans = 0x7777;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans->div = q;
    ans->mod = n;
    return ans;
}

void print_int(int num) {
    struct DivMod* ans;
    char buffer[10];
    int i;
    for (i = 0; i < 10; i++) {
        buffer[i] = '\0';
    }
    i = 0;
    do {
        ans = divmod(num, 10);
        buffer[i] = '0' + ans->mod;
        i++;
        num = ans->div;
    } while (num > 0);
    strrev(buffer);
    puts(buffer);
}

void main() {
    print_int(420);
}