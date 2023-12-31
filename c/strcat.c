#include "bit16lib.h"

char* test = "Hello, ";

char* strcat(const char* s, const char* t) {
    int i; int j;
    i = j = 0;
    while (s[i] != '\0') 
        i++;
    while((s[i++] = t[j++]) != '\0')
        ;
}

void main() {
    char* test2 = "world!";
    strcat(test, test2);
    println(test);
}