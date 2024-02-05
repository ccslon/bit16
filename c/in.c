#include <stdio.h>

void main() {
    while (1) {
        char c = getc(&stdin);
        if (c) {
            putchar(c);
        }
    }
}