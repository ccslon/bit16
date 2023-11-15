#define div_t struct div_t
div_t {
    int quot;
    int rem;
};
div_t div(int num, int den) {
    div_t ans;
    int quot = 0;
    while (num >= den) {
        num -= den;
        quot++;
    }
    ans.quot = quot;
    ans.rem = num;
    return ans;
}
int not_(int num) {
    return num == 0;
}
int abs(int num) {
    if (num < 0) return -num;
    return num;
}
int rand() {}
int srand(int seed) {}
int atoi(char* str) {
    int num = 0;
    while (*str != '\0') {
        num *= 10;
        num += *str - '0';
        str++;
    }
    return num;
}
void* calloc(int nitems, int size) {}
void free(void* ptr) {}
void* malloc(int size) {}
void* realloc(void* ptr, int size) {}