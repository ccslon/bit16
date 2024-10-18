#define NULL (void*)0
typedef unsigned int size_t;
typedef struct {
    int quot;
    int rem;
} div_t;
div_t div(int num, int den) {
    div_t ans = {num / den, num % den};
    return ans;
}
int abs(int n) {
    if (n < 0) return -n;
    return n;
}
int bsearch(void* x, void* v, size_t size, int n, int (*cmp)(void*, void*)) {
    int low = 0;
    int mid;
    int high = n - 1;
    while (low <= high) {
        mid = low + (high - low) / 2;
        int cond = (*cmp)(x, &v[mid*size]);
        if (cond < 0)
            high = mid - 1;
        else if (cond > 0) 
            low = mid + 1;
        else
            return mid;
    }
    return -1;
}
void swap(void* v, size_t size, int i, int j) {
    char t;
    unsigned k;
    for (k = 0; k < size; k++) {
        t = *(char*)(v+i*size+k);
        *(char*)(v+i*size+k) = *(char*)(v+j*size+k);
        *(char*)(v+j*size+k) = t;
    }
}
void qsort(void* v, unsigned size, int left, int right, int (*cmp)(void*,void*)) {
    int i, last;
    if (left >= right)
        return;
    int mid = left + (right - left) / 2;
    swap(v, size, left, mid);
    last = left;
    for (i = left+1; i <= right; i++)
        if ((*cmp)(&v[i*size], &v[left*size]) < 0)
            swap(v, size, ++last, i);
    swap(v, size, left, last);
    qsort(v, size, left, last-1, cmp);
    qsort(v, size, last+1, right, cmp);
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
    int i, n = 0;
    for (i = 0; '0' <= s[i] && s[i] <= '9'; ++i)
        n = 10 * n + (s[i] - '0');
    return n;
}
#define HEAPLEN 256
char heap[HEAPLEN];
char* heapindex = 0;
void* malloc(size_t size) {
    if (heapindex >= HEAPLEN) 
        return NULL;
    void* p = &heap[heapindex];
    heapindex += size;
    return p;
}
void free(void* p) {}
void* realloc(void* p, size_t size) {
    void* d = malloc(size);
    size_t i;
    for (i = 0; i < size; i++) {
        *(char*)(d+i) = *(char*)(p+i);
    }
    free(p);
    return d;
}
void* calloc(size_t n, size_t size) {
    size_t words = n*size;
    size_t i;
    void* p = malloc(words);
    for (i = 0; i < words; i++)
        *(char*)(p+i) = 0;
    return p;
}