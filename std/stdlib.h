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
//bsearch(...)
void swap(int* v, int i, int j) {
    int t;
    t = v[i];
    v[i] = v[j];
    v[j] = t;
}
void qsort(int* v, int l, int r) {
    int i; int t;
    if (l >= r)
        return;
    swap(v, l, (l + r) >> 1); // (l+r) / 2 
    t = l;
    for (i = l+1; i <= r; i++)
        if (v[i] < v[l])
            swap(v, ++t, i);
    swap(v, l, t);
    qsort(v, l, t-1);
    qsort(v, t+1, r);
}
int next = 0;
int rand() {
    next = 81 * next + 79; // % 2**16
    return next;
}
void srand(int seed) {
    next = seed;
}
int atoi(const char* s) {
    int i;
    int n = 0;
    for (i = 0; '0' <= s[i] && s[i] <= '9'; ++i)
        n = 10 * n + (s[i] - '0');
    return n;
}
void* calloc(int nitems, int size) {}
void free(void* ptr) {}
void* malloc(int size) {}
void* realloc(void* ptr, int size) {}