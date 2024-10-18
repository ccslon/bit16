#define LIM 5
int ack(int m, int n) {
    if (m == 0) {
        return n + 1;
    } else if (n == 0) {
        return ack(m - 1, 1);
    } else {
        return ack(m - 1, ack(m , n-1));
    }
}
int main() {
    int i, j;
    for (i = 0; i < LIM; i++) {
        for (j = 0; j < LIM; j++) {
            ack(i, j);
        }
    }
    return 0;
}