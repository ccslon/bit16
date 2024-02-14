#define N 10
#define inc(n) (n++)
#define min(a, b) (a > b ? b : a)
#define range(i, n) ((i) = 0; (i) < (n); (i)++)

void test() {
    int i;
    int minN;
    for range(i, N) {
        minN = min(minN, i);
        inc(minN);
    }
}