#include <stdio.h>

void setup();
void loop(char c);

void main() {
    setup();
    char* in = (char*)INPORT;
    while (1) {
        char c = *in;
        if (c) {
            putchar(c);
            fputc(c, &stdin);
            loop(c);
        }
    }
}