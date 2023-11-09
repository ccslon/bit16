int n = 0;
void main(int argc, char **argv) {
    n[p] = 3 / 4;
    if (n > 0) {
        foo();
    } else {
        bar();
    }
    int i;
    while (n == 0x33) {
        int* j = (int)baz();
        struct My my;
    }
}

struct My;
struct My {
    int thing;
    char d = 'd';
    char *lol = "lol";
};

struct My* foo() {
    return;
}

void expr() {
    term();
    while (peek('+') || peek('-')) {
        next();
        term();
    }
}

int OUT = 0x7fff;
void put(char c) {
    *OUT = chr;
}
void print(char *str) {
    while (*str != '\0') {
        put(*str);
        str++;
    }
}
void main() {
    print("Hello world!");
}

int fact(int n) {
    if (n == 0) {
        return 1;
    }
    return n * fact(n-1);
}
int fib(int n) {
    if (n == 1) {
        return 0;
    } else if (n == 2) {
        return 1;
    } else {
        return fib(n-1) + fib(n-2);
    }    
}
int abs(int n) {
    if (n < 0) return -n;
    return n;
}
int div(int n, int d) {
    int q = 0;
    while (n >= d) {
        n -= d;
        q++;
    }
    return q;
}
int mod(int n, int d) {
    while (n >= d) {
        n -= d;
    }
    return n;
}
int pow(int b, int e) {
    int p = 1;
    while (e > 0) {
        p *= b;
        e -= 1;
    }
    return p;
}