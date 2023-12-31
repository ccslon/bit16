#include "bit16lib.h"
#define va_list void*
#define va_start(ap, last) (ap = _VARLIST_)
#define va_arg(ap, type) (ap++) // add cast
#define va_end(ap) (op = 0)

int sum(int n, ...) {
    va_list ap;
    va_start(ap, n);
    int i;
    int sum = 0;
    for (i = 0; i < n; i++) {
        sum += va_arg(ap, int);
    }
    return sum;
}

void printf(char* fmt, ...) {

}

void main() {
    printint(34); //sum(3, 1, 2, 3));
    put('\n');
    /*
    printint(sum(1, 1));
    put('\n');
    printint(sum(4, 1,2,3,4));
    put('\n');*/
}