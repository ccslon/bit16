#include "bit16lib.h"
#define va_list void*
#define va_start(ap, last) (ap = _VARLIST_)
#define va_arg(ap, type) ((type)*ap++) // add cast
#define va_end(ap) (ap = 0)

int sum(int n, ...) {
    va_list ap;
    va_start(ap, n);
    int i;
    int sum = 0;
    for (i = 0; i < n; i++) {
        sum += va_arg(ap, int);
    }
    va_end(ap);
    return sum;
}


void main() {
    printint(sum(3, 1, 2, 3));
    put('\n');
    printint(sum(4, 1, 2, 3, 4));
    put('\n');
    printint(sum(1, 1));
    put('\n');
}