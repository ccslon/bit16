int dofib(const int n, const int a, const int b) {
    switch (n) {
        case 1: return a;
        case 2: return b;
        default: {
            return dofib(n-1, b, a+b);
        }
    }
}
int tailfib(const int n) {
    return dofib(n, 0, 1);
}
void main() {
    tailfib(3);
}
/*
LR
B
C
1
0
B: 1
LR
D



*/