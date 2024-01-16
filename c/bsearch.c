#include <stdlib.h>
#include <stdio.h>

#define N 7

int arr[6] = {1,2,3,4,4,6};

void main() {
    int i;
    int loc;
    for (i = 0; i < N; i++) {
        loc = bsearch(i, arr, 6);
        printf("%d\n", loc);
        //printf("%d\n", bsearch(i, arr, 6));
    }
}