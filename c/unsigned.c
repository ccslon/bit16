#include <stdio.h>
typedef unsigned int size_t;

int main() {
    unsigned int u[5] = {0, 1, 2, 3, 1};
    int i[4] = {-1, 0, 1, 2};
    
    //u vs u
    printd(u[1] == u[4]);
    printd(u[2] != u[4]);
    printd(u[2] > u[1]);
    printd(u[0] < u[4]);
    printd(u[2] >= u[1]);
    printd(u[1] >= u[4]);
    printd(u[0] <= u[4]);
    printd(u[1] <= u[4]);
    if (u[2] > u[1]) {
        putchar('1');
    }
    putchar(' ');
    //printd(i[3] == u[2]);
    //printd(i[0] != u[2]);
    printd(i[3] > u[1]);
    printd(i[0] < u[0]);
    printd(i[3] >= u[1]);
    printd(i[0] <= u[0]);
    printd(i[3] >= u[2]);
    printd(i[3] <= u[2]);
    printd(i[0] > u[0]);
    size_t j;
    for (j = 0; j < 10; j++) {
        printd(j);
    }
}