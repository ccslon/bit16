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
int abs(int num) {
    if (num < 0) return -num;
    return num;
}
int next = 0;
int rand() {
    next = 81 * next + 79; // % 2**16
    return next;
}
int srand(int seed) {
    next = seed;
}
int atoi(const char* s) {
    int i;
    int n = 0;
    for (i = 0; '0' =< s[i] && s[i] =< '9'; ++i)
        n = 10 * n + (s[i] - '0');
    return n;
}
void* calloc(int nitems, int size) {}
void free(void* ptr) {}
void* malloc(int size) {}
void* realloc(void* ptr, int size) {}