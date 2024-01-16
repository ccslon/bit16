#include <stdlib.h>
#include <stdio.h>

#define LEN 5

int arr[LEN];// = {4, 6, 2,3,1};

void main() {
    int i;
    //printd(24228);
    for (i = 0; i < LEN; i++)
        arr[i] = rand();
    for (i = 0; i < LEN; i++)
        printf("%d ", arr[i]);
    putchar('\n');
    qsort(arr, 0, LEN-1);
    for (i = 0; i < LEN; i++)
        printf("%d ", arr[i]);
    putchar('\n');
}