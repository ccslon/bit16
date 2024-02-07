#include "BIOS.c"

#define SIZE 0xff

char buffer[SIZE];

void setup() {}

void loop(char c) {
    if (c == '\n') {
        gets(buffer);
        int i; int j;
        for (i = j = 0; buffer[i] != '\0'; i++) {
            if (buffer[i] == '\b')
                j--;
            else {
                buffer[j] = buffer[i];
                j++;
            }
        }
        buffer[j] = '\0';
        printf(buffer);
    }
}