#include <stdlib.h>
#include <stdio.h>

#define LEN 10

int arr[LEN];

void main() {
    int i;
    printd(24228);
    for (i = 0; i < LEN; i++)
        arr[i] = rand();
    for (i = 0; i < LEN; i++)
        printf("%d ", arr[i]);
    putchar('\n');
}