int foo(int a, int b, int c, int d) {
    c = 0;
    d = 1;
}

int bar() {
    return foo(1, 2, 3, 4);
}

int baz() {
    return 3 + foo(1,2,3,4);
}

int fib(int n) { //36.24
    switch (n) {
        case 1: return 0;
        case 2: return 1;
        default: return fib(n-1) + fib(n-2);
    }
}

int not(int n) {
    return !n;
}

int not2(int n) {
    if (!n)
        return 123;
    return 9;
}

/*
foo:
    

bar:
    ...
    sub SP, 3
    mov A, 1
    ld [SP, 0], A
    mov A, 2
    ld [SP, 1], A
    mov A, 3
    ld [SP, 2], A
    call foo
    ...
*/