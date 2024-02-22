#include <stdio.h>

void setup() {}
void loop(char c) {}

void main() {
    setup();
    char* in = (char*)INPORT;
    while (1) {
        char c = *in;
        if (c) {
            stdout.buffer[stdout.write] = c;
            stdout.write++;
            stdin.buffer[stdin.write] = c;
            stdin.write++;
            loop(c);
        }
    }
}