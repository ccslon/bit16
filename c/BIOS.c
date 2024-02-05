#include <stdio.h>

void iter(char c);

void main() {
    while (1) {
        char c = *stdin.buffer;
        if (c) {
            fputc(c, &stdin);
            putchar(c);
            iter(c);
        }
    }
}