#include <stdio.h>
char* gptr = "Hello global*\n";
char garr[16] = "Hello global[]\n";

int main() {
    char* ptr = "Hello stack*\n";
    char arr[] = "Hello stack[]\n";
    printf("Hello cstrings!\n");
    printf(gptr);
    printf(garr);
    printf(ptr);
    printf(arr);
}