#define NULL (void*)0
typedef struct _div_t_ {
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
int bsearch(int x, int* v, int n, int (*cmp)(int, int)) {
    int low = 0;
    int mid;
    int high = n - 1;
    while (low <= high) {
        mid = low + (high - low) / 2;
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
    int i, last;
    if (left >= right)
        return;
    swap(v, left, left + (right - left) / 2);
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
    int i, n = 0;
    for (i = 0; '0' <= s[i] && s[i] <= '9'; ++i)
        n = 10 * n + (s[i] - '0');
    return n;
}
struct header {
    struct header *next;
    int size;
};
typedef struct header Header;
Header *freep = NULL;
Header base;
void* calloc(int nitems, int size) {}
void free(void* ptr) {
    Header *bp, *p;
    bp = (Header*)ptr - 1;
    for (p = freep; !(p < bp && bp < p->next); p = p->next)
        if (p >= p->next && (p < bp || bp <p->next))
            break;
    if (bp + bp->size == p->next) {
        bp->size += p->next->size;
        bp->next = p->next->next;
    } else 
        bp->next = p->next;
    if (p + p->next == bp) {
        p->size += bp->size;
        p->next = bp->next;
    } else
        p->next = bp;
    freep = p;
}
void* malloc(int size) {
    Header *p, *prevp;
    if ((prevp = freep) == NULL) {
        base.next = freep = prevp = &base;
        base.size = 0;
    }
    for (p = prevp->next; 1; prevp = p, p = p->next) {
        if (p->size >= size) {
            if (p->size == size)
                prevp->next = p->next;
            else {
                p->size -= size;
                p += p->size;
                p->size = size;
            }
            freep = prevp;
            return (void*)(p+1);
        }
    }
}
void* realloc(void* ptr, int size) {}