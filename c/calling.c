#define LEN 5

int bsearch(int x, int* v, int n) {
    return 0;
}

void printf(const char* format, ...) {

}


int arr[LEN];

void main() {
    int i;
    int loc;
    for (i = 0; i < LEN; i++) {
        loc = bsearch(i, arr, 6);
        printf("%d\n", loc);
    }
pause:
    for (i = 0; i < LEN; i++) {
        printf("%d\n", bsearch(i, arr, LEN));
    }
}