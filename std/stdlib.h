#include <string.h>
struct div_t {
    int quot;
    int rem;
};
struct div_t div(int num, int den) {
    struct div_t ans;
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    ans.quot = q;
    ans.rem = n;
    return ans;
}
int not(int num) {
    return num == 0;
}
int abs(int num) {
    if (num < 0) return -num;
    return num;
}
int rand() {

}
int srand(int seed) {
    
}

int atoi(char* str) {
    str = strrev(str);
    int place = 1;
    int num = 0;
    while (*str != '\0') {
        num += place * (*str - '0');
        place *= 10;
        str++;
    }
    return num;
}
void* calloc(int nitems, int size) {

}
void free(void* ptr) {

}
void* malloc(int size) {

}
void* realloc(void* ptr, int size) {

}