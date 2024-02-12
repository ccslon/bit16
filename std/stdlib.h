typedef struct _div_t_ {
    int quot;
    int rem;
} div_t;
div_t div(int num, int den) {
    div_t ans;
    int quot = 0;
    int rem = 0;
    int i;
    for (i = 15; i >= 0; i--) {
        rem <<= 1;
        rem |= (num >> i) & 1;
        if (rem >= den) {
            rem -= den;
            quot |= (1 << i);
        }
    }
    ans.quot = quot;
    ans.rem = rem;
    return ans;
}
int abs(int n) {
    if (n < 0) return -n;
    return n;
}
int bsearch(int x, int* v, int n, int (*cmp)(int, int)) {
    int low = 0;
    int mid;
    int high = n - 1;
    while (low <= high) {
        mid = low + ((high - low) >> 1);
        int cond = (*cmp)(x, v[mid]);
        if (cond < 0)
            high = mid - 1;
        else if (cond > 0) 
            low = mid + 1;
        else
            return mid;
    }
    return -1;
}
void swap(int* v, int i, int j) {
    int t;
    t = v[i];
    v[i] = v[j];
    v[j] = t;
}
void qsort(int* v, int left, int right, int (*cmp)(int, int)) {
    int i; int last;
    if (left >= right)
        return;
    swap(v, left, (left + right) >> 1); // (l+r) / 2 
    last = left;
    for (i = left+1; i <= right; i++)
        if ((*cmp)(v[i], v[left]) < 0)
            swap(v, ++last, i);
    swap(v, left, last);
    qsort(v, left, last-1, cmp);
    qsort(v, last+1, right, cmp);
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